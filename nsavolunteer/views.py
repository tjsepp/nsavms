from django.shortcuts import render,get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, \
        ListView, DeleteView,TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.template import RequestContext
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from forms import LoginForm, UserProfileForm,FamilyProfileForm,PasswordChangeFormExtra, \
    StudentUpdateForm, AddUserEventForm,AddNewFamily,AddFamilyVolunteers,\
    AddTrafficVolunteersForm,AddNewVolunteersToFamily,PasswordRecoveryForm
from .models import *
from django.forms.formsets import formset_factory
from django.db.models import Sum, Prefetch
from nsaSchool.models import VolunteerNews, SchoolYear
from authtools.forms import UserCreationForm
from nsaEvents.models import EventTasks
import json
from django.contrib.auth.models import Group



def homeView(request):
    news = VolunteerNews.objects.all()
    response = render(request, 'home.html')
    return response


class LoginView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('userVolunteerData')


    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user )
        return super(LoginView, self).form_valid(form)


class LogoutView(RedirectView):
    permanent = False
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView,self).get(request,args,kwargs)


class ChangePassword(LoginRequiredMixin, FormView):
    template_name = 'account/changePassword.html'
    form_class = PasswordChangeFormExtra
    success_url = reverse_lazy('userVolunteerData')

    def  get_form(self, form_class):
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self,form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(ChangePassword,self).form_valid(form)


class PasswordRecoveryView(FormView):
    template_name = 'account/password_recovery.html'
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy('mainlogin')

    def form_valid(self, form):
        form.reset_email()
        return super(PasswordRecoveryView,self).form_valid(form)


def VolunteerIndex(request):
    '''
    This view populates the volunteerIndex table with all active users
    '''
    volunteerIndex = User.objects.all().select_related('linkedUser','linkedUser__volunteerType').\
        prefetch_related('linkedUser__interest','family','groups').filter(is_active=True)
    response = render(request, 'tables/volunteerIndex.html',{'volunteerIndex':volunteerIndex})
    return response


def InactiveVolunteerIndex(request):
    '''
    This view populates the volunteerIndex table with all active users
    '''
    volunteerIndex = User.objects.all().select_related('linkedUser','linkedUser__volunteerType').\
        prefetch_related('linkedUser__interest','family','groups')
    response = render(request, 'tables/volunteerIndex.html',{'volunteerIndex':volunteerIndex})
    return response


def FamilyIndex(request):
    FamilyIndex = FamilyProfile.objects.all().prefetch_related('famvolunteers','students')
    response = render(request, 'tables/FamilyIndex.html',{'FamilyIndex':FamilyIndex})
    return response


class Report_Family_Hours_Current(ListView):
    model = FamilyProfile
    paginate_by = 100
    queryset = FamilyProfile.objects.prefetch_related('famvolunteers','students','familyAgg','familyAgg__schoolYear').order_by('familyName')
    context_object_name = "FamilyIndex"
    template_name="reports/totalFamilyHours.html"


def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''

    curYear = SchoolYear.objects.get(currentYear = 1)
    curUser = User.objects.prefetch_related('linkedUser','linkedUser__linkedUserAccount__volunteerhours_set',
                                            'linkedUser__linkedUserAccount__family','linkedUser__linkedUserAccount__rewardCardValue').get(pk=request.user.id)
    rewardCardData = curUser.rewardCardValue.filter(schoolYear = curYear).order_by('-refillDate')
    volhours = curUser.volunteerhours_set.select_related('event','family').filter(schoolYear=curYear).all().order_by('-eventDate')
    traffic = curUser.trafficDutyUser.filter(schoolYear = curYear).order_by('-trafficDutyDate')
    rewardCardSum =curUser.rewardCardValue.filter(schoolYear = curYear).aggregate(Sum('volunteerHours')).values()[0]
    parkingDutySum=curUser.trafficDutyUser.filter(schoolYear = curYear).aggregate(Sum('volunteerHours')).values()[0]
    volunteerHoursSum=volhours.filter(approved=True).aggregate(Sum('volunteerHours')).values()[0]
    if rewardCardSum==None:
        rewardCardSum=0
    if volunteerHoursSum ==None:
        volunteerHoursSum = 0
    if parkingDutySum==None:
        parkingDutySum=0
    familySums = curUser.family.all()
    totalVolunteerHoursUser = rewardCardSum+volunteerHoursSum+parkingDutySum
    histHours = curUser.linkedUser.historical_volunteer_data
    hasInterests = curUser.linkedUser.interest.count()
    if curUser.family.count()>1:
        multFam = True
    else:
        multFam = False

    response = render(request, 'volunteerData/volunteerData.html',{'rewardCardData':rewardCardData,
         'volHours':volhours,'rewardCardSum':rewardCardSum,'volunteerHoursSum':volunteerHoursSum,
        'familySums':familySums,'totalVolunteerHoursUser':totalVolunteerHoursUser,'multFam':multFam,
        'curYear':curYear,'curUser':curUser,'histHours':histHours,'hasInterests':hasInterests,'traffic':traffic})
    return response



@login_required
def userSettings(request):
    #profile = VolunteerProfile.objects.get_or_create(linkedUserAccount = request.user)
    #cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get_or_create(linkedUserAccount= auth)
    cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType').prefetch_related('interest').get(linkedUserAccount= request.user)
    userFamily = FamilyProfile.objects.filter(famvolunteers = request.user).all()
    rewardCards = RewardCardUsers.objects.filter(linkedUser=request.user).all()
    response = render(request, 'userprofile/userprofile.html',{'cur_user':cur_user,'userFamily':userFamily,'rewardCards':rewardCards})
    return response


class UpdateVolunteerProfile(LoginRequiredMixin,UpdateView):
    form_class = UserProfileForm
    template_name = 'forms/updateVolunteerProfile.html'

    def get_object(self):
        if 'volid' in self.kwargs:
            return VolunteerProfile.objects.get(linkedUserAccount=self.kwargs['volid'])
        else:
            return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        if 'famid' in self.kwargs:
            return reverse('familyprofile', kwargs={'famid':self.kwargs['famid']})
        else:
            return reverse('user_profile')

    def get_context_data(self, **kwargs):
        context = super(UpdateVolunteerProfile, self).get_context_data(**kwargs)
        context['interests'] = VolunteerInterests.objects.filter(active=True).all()
        context['profileInt'] = self.object.interest.all()
        return context


def FamilyProfilePage(request, famid):
    '''This takes an argument of a family ID and provides all family level information
    '''
    family = FamilyProfile.objects.prefetch_related('famvolunteers','famvolunteers__linkedUser','students'
                                                    ,'famvolunteers__linkedUser__volunteerType','students__teacher',
                                                   'famvolunteers__linkedUser__interest','students__grade' ).get(pk=famid)

    return render_to_response('userprofile/familyProfile.html',{'family':family},context_instance=RequestContext(request))


class UpdateFamilyProfile(LoginRequiredMixin,UpdateView):
    form_class = FamilyProfileForm
    template_name = 'forms/updateFamilyProfile.html'

    def get_object(self):
        return FamilyProfile.objects.get(pk=self.kwargs['famId'])
        #return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        return reverse('user_profile')

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateFamilyProfile, self).get_context_data(*args, **kwargs)
        context['familyName'] = FamilyProfile.objects.get(pk=self.kwargs['famId']).familyName
        #context['familyName'] = 'Testing'
        return context

    def form_valid(self, form):
        family_mod = form.save(commit=False)
        family_mod.save()
        StudentToFamily.objects.filter(group = family_mod).all().delete()
        for student in form.cleaned_data.get('students'):
            famStudents = StudentToFamily(group=family_mod,student = student)
            famStudents.save()
        return HttpResponseRedirect(self.get_success_url())


class UpdateStudent(LoginRequiredMixin,UpdateView):
    form_class = StudentUpdateForm
    template_name = 'forms/studentUpdate.html'

    def get_object(self):
        return Student.objects.get(pk=self.kwargs['stuId'])

    def get_success_url(self):
        return reverse('user_profile')




class logUserHours(LoginRequiredMixin, CreateView):
    form_class = AddUserEventForm
    template_name = 'forms/addVolunteerHours.html'


    def get_success_url(self):
        if self.request.POST.get('save'):
             retPage = 'userVolunteerData'
        elif self.request.POST.get('saveAndAdd'):
             retPage = 'logUserHours'
        return reverse(retPage)

    def get_initial(self):
        return {
            'volunteer':self.request.user
        }

    def form_valid(self, form):
        form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
        #form.save()
        return super(logUserHours,self).form_valid(form)

    def get_context_data(self,*args, **kwargs):
        context = super(logUserHours,self).get_context_data(*args, **kwargs)
        context['schoolYear'] = SchoolYear.objects.get(currentYear=1)
        context['tasks'] = ', '.join("'{0}'".format(x[0]) for x in EventTasks.objects.all().values_list('taskName'))
        return context

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(logUserHours, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = self.request.user)
        kwargs['user'] = self.request.user
        return kwargs


@login_required
def deleteLoggedHours(request, vhoursID):
    obj = VolunteerHours.objects.get(pk=vhoursID)
    if not obj.volunteer == request.user:
            return HttpResponseRedirect(reverse('userVolunteerData'))
    obj.delete()
    return HttpResponseRedirect(reverse('userVolunteerData'))


class updateUserHours(LoginRequiredMixin,UpdateView):
    form_class = AddUserEventForm
    template_name = 'forms/addVolunteerHours.html'

    def get_object(self, queryset=None):
        return VolunteerHours.objects.get(pk=self.kwargs['vhoursID'])


    def form_valid(self, form):
        form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
        #form.save()
        return super(updateUserHours,self).form_valid(form)

    def get_context_data(self,*args, **kwargs):
        context = super(updateUserHours,self).get_context_data(*args, **kwargs)
        context['schoolYear'] = SchoolYear.objects.get(currentYear=1)
        return context

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(updateUserHours, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = self.request.user)
        kwargs['user'] = self.request.user
        return kwargs


    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'userVolunteerData'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'logUserHours'
        return reverse(retPage)


def addInterestToProfile(request,Intid):
    profile = get_object_or_404(VolunteerProfile,linkedUserAccount=request.user)
    interest = VolunteerInterests.objects.get(pk=Intid)
    interest.profile_interest.add(profile)
    interest.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    #return HttpResponseRedirect(querysnippet.get_absolute_url())
addInterestToProfile = login_required(addInterestToProfile)


def deleteInterestFromProfile(request,Intid):
    profile = get_object_or_404(VolunteerProfile,linkedUserAccount=request.user)
    interest = VolunteerInterests.objects.get(pk=Intid)
    interest.profile_interest.remove(profile)
    interest.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    #return HttpResponseRedirect(querysnippet.get_absolute_url())
deleteInterestFromProfile = login_required(deleteInterestFromProfile)


class CreateFamily(CreateView):
    form_class = AddNewFamily
    template_name = 'forms/addNewFamily.html'
    famid = None

    def get_success_url(self):
        return reverse('addusertofamily', kwargs={'famid': self.famid})

    def form_valid(self, form):
        fam = form.save()
        self.famid = fam.familyProfileId
        return super(CreateFamily, self).form_valid(form)


def AddVolunteersToNewFamily(request,famid):
    family = FamilyProfile.objects.get(pk=famid)
    familyname = family.familyName
    addVolunteerFormset = formset_factory(AddFamilyVolunteers, extra=1)
    formset=addVolunteerFormset(request.POST)
    if request.method =="POST":
        if formset.is_valid() :
            for form in formset:
                form.save()
                family.famvolunteers.add(form.instance)
                family.save()
            if 'saveFamily' in request.POST:
                return HttpResponseRedirect(reverse_lazy('familyIndex'))
            elif 'saveAndAdd' in request.POST:
                return HttpResponseRedirect(reverse_lazy('addfamily'))
        else:
            form_errors = formset.errors
            return render_to_response('forms/addUsersToFamily.html',{'formset':formset,'familyName':familyname,'famid':famid, 'form_errors':form_errors}, context_instance=RequestContext(request))
    else:
        return render_to_response('forms/addUsersToFamily.html',{'formset':addVolunteerFormset(),'familyName':familyname,'famid':famid},
                                  context_instance=RequestContext(request))


def ProcessContactToExistingFamily(request, famid):
    '''
    This view takes a familyID and email address from modal dialog, searches to see
    if user exists. If so, creates relationship between family and volunteer. If not, it will
    create a new user and add them to the family.
    '''
    family = FamilyProfile.objects.get(pk= famid)
    contact = User.objects.filter(email=request.GET['emailaddress']).exists()
    if contact:
        family.famvolunteers.add(User.objects.get(email=request.GET['emailaddress']))
        family.save()
        return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid': famid}))
    else:
        return redirect('addContactToExistingFamily', str(famid))


def addContactToExistingFamily(request,famid):
     family = FamilyProfile.objects.get(pk= famid)
     if request.method=='POST':
            form =AddNewVolunteersToFamily(data=request.POST)
            if form.is_valid():
                volunteer = form.save(commit=False)
                form.save()
                family.famvolunteers.add(volunteer)
                return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid': famid}))
     else:
        form = AddNewVolunteersToFamily()
     return render_to_response('forms/addNewUserToFamily.html',{'form':form}, context_instance=RequestContext(request))


def addVolunteer_woFamily(request):
     if request.method=='POST':
        form =AddNewVolunteersToFamily(data=request.POST)
        if form.is_valid():
            volunteer = form.save(commit=False)
            form.save()
            return HttpResponseRedirect(reverse('volunteerIndex'))
     else:
        form = AddNewVolunteersToFamily()
     return render_to_response('forms/addNewUserToFamily.html',{'form':form}, context_instance=RequestContext(request))


def RemoveContactFromFamily(request,famid,volunteerid):
    family = FamilyProfile.objects.get(pk= famid)
    volunteer = User.objects.get(pk = volunteerid)
    family.famvolunteers.remove(volunteer)
    family.save()
    return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid': famid}))


def AddTrafficVolunteers(request):
    addVolunteerFormset = formset_factory(AddTrafficVolunteersForm, extra=1)
    formset=addVolunteerFormset(request.POST )
    if request.method =="POST":
        if formset.is_valid() :
            message="Thank You!"
            for form in formset:
                form.save(commit=False)
                form.instance.linkedFamily = FamilyProfile.objects.filter(famvolunteers =form.instance.volunteerId)[0]
                form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
                form.save()
            return HttpResponseRedirect(reverse_lazy('trafficReport'))
        else:
            form_errors = formset.errors
            return render_to_response('forms/addTrafficVolunteers.html',{'formset':formset,'form_errors':form_errors}, context_instance=RequestContext(request))
    else:
        return render_to_response('forms/addTrafficVolunteers.html',{'formset':addVolunteerFormset()},
                                  context_instance=RequestContext(request))


def YearEndProcess(request):
    '''
    This process will update all volunteerProfiles and mark them as pending.
    It will also increment all childrens grade one position up. The student update is done via methon
    on the Student model
    '''
    VolunteerProfile.objects.update(volStatus='pending')
    activeStudents = Student.objects.filter(activeStatus=True)
    for t in activeStudents:
        t.newYear()


def deactivateFullFamily(request, famid):
    pass


class TrafficReport(TemplateView):

    template_name = "tables/trafficDuty.html"

    def get_context_data(self, **kwargs):
        context = super(TrafficReport, self).get_context_data(**kwargs)
        context['recentTraffic'] = TrafficDuty.objects.all().order_by('-dateCreated')[:50]
        return context


def markAsPending(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerProfile.objects.get(pk=vol)
        ur.volStatus = 'pending'
        ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def markAsApproved(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerProfile.objects.get(pk=vol)
        if ur.linkedUserAccount.is_active:
            ur.volStatus = 'approved'
            ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def deactivateVolunteerAccount(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerProfile.objects.get(pk=vol)
        if ur.linkedUserAccount.is_active==True:
            if ur.linkedUserAccount.is_superuser == False:
                ur.linkedUserAccount.is_active = False
                ur.linkedUserAccount.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def activateVolunteerAccount(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerProfile.objects.get(pk=vol)
        if ur.linkedUserAccount.is_active==False:
            ur.linkedUserAccount.is_active = True
            ur.linkedUserAccount.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def markAsAvc(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        volunteer = User.objects.get(pk = VolunteerProfile.objects.get(pk=vol).linkedUserAccount_id)
        g = Group.objects.get(name='AVC')
        g.user_set.add(volunteer)
        g.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def removeFromAvc(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        volunteer = User.objects.get(pk = VolunteerProfile.objects.get(pk=vol).linkedUserAccount_id)
        g = Group.objects.get(name='AVC')
        g.user_set.remove(volunteer)
        g.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def get_tasks(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        tasks = EventTasks.objects.filter(taskName__icontains = q )[:20]
        results = []
        for task in tasks:
            task_json = {}
            task_json['id'] = task.taskid
            task_json['label'] = task.taskName
            task_json['value'] = task.taskName
            results.append(task_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    return HttpResponse(data, content_type="application/json")


def hoursToApprove(request):
    hours_to_approve = VolunteerHours.objects.prefetch_related('volunteer','family','event').filter(approved=False)
    response = render(request, 'tables/hoursToApprove.html',{'hours_to_approve':hours_to_approve})
    return response


def approvedHours(request,vhId):
    rec = VolunteerHours.objects.get(pk=vhId)
    rec.approved =True
    rec.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def get_students(request, famid):
    if request.is_ajax():
        q = request.GET.get('search_text', '')
        existing = FamilyProfile.objects.get(pk=famid)
        students = Student.objects.filter(studentLastName__icontains = q).filter(activeStatus=True).exclude(studentId__in=existing.students.all().values('studentId'))
        #students = Student.objects.filter(studentLastName__icontains = q).filter(activeStatus=True)
        family = FamilyProfile.objects.get(pk=famid)
    return render_to_response('forms/addStudentSubTemplate.html',{'results':students,'family':family})


def addStudentToFamily(request,stuid,famid):
     fam = FamilyProfile.objects.get(pk= famid)
     stu = Student.objects.get(pk=stuid)
     newRec = StudentToFamily.objects.get_or_create(student=stu,group=fam)
     return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid':famid}))


def RemoveStudentFromFamily(request,famid,stuid):
    fam= FamilyProfile.objects.get(pk= famid)
    stu = Student.objects.get(pk = stuid)
    stuToFam = StudentToFamily.objects.get(student=stu,group = fam).delete()
    return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid': famid}))


class addNewStudent(LoginRequiredMixin, CreateView):
    form_class = StudentUpdateForm
    template_name = 'forms/addStudent.html'


    def get_success_url(self):
        famid=self.kwargs['famid']
        print famid
        return reverse('familyprofile', kwargs={'famid': famid})

    def form_valid(self, form):
        stu = form.save()
        fam = FamilyProfile.objects.get(pk=self.kwargs['famid'])
        famRelate = StudentToFamily.objects.create(student=stu, group=fam)
        famRelate.save()
        return super(addNewStudent,self).form_valid(form)



