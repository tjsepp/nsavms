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
    AddNewVolunteersToFamily,PasswordRecoveryForm,AddInterestForm, RecruitingEmailForm,EditVolunteersLogin,\
    TrafficWeeklyUpdate,DeclineLoggedHours,upLoadRewardCardUsers,upLoadRewardCardPurchaseData
from .models import *
from django.forms.formsets import formset_factory
from django.db.models import Sum
from nsaSchool.models import VolunteerNews, SchoolYear
from nsaEvents.models import EventTasks
import json
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage, send_mail
import requests
from django.conf import settings
import  datetime
from operator import itemgetter


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

def PendingVolunteerIndex(request):
    '''
    This view populates the volunteerIndex table with all active users
    '''
    volunteerIndex = User.objects.select_related('linkedUser','linkedUser__volunteerType').\
        prefetch_related('linkedUser__interest','family','groups').filter(is_active=True).filter(linkedUser__volStatus='pending')
    response = render(request, 'tables/volunteerIndex.html',{'volunteerIndex':volunteerIndex})
    return response


def InactiveVolunteerIndex(request):
    '''
    This view populates the volunteerIndex table with all inactive users
    '''
    volunteerIndex = User.objects.filter(is_active=False).select_related('linkedUser','linkedUser__volunteerType').\
        prefetch_related('linkedUser__interest','family','groups')
    response = render(request, 'tables/volunteerIndex.html',{'volunteerIndex':volunteerIndex})
    return response


def FamilyIndex(request):
    FamilyIndex = FamilyProfile.objects.all().prefetch_related('famvolunteers','students').order_by('familyName')
    response = render(request, 'tables/FamilyIndex.html',{'FamilyIndex':FamilyIndex})
    return response

def InterestIndex(request):
    interestIndex = VolunteerInterests.objects.all()
    response = render(request, 'tables/interestIndex.html',{'interestIndex':interestIndex})
    return response


class Report_Family_Hours_Current(ListView):
    model = FamilyProfile
    paginate_by = 100
    queryset = FamilyProfile.objects.prefetch_related('famvolunteers','students','familyAgg','familyAgg__schoolYear').order_by('familyName')
    context_object_name = "FamilyIndex"
    template_name="reports/totalFamilyHours.html"

@login_required
def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''

    curYear = SchoolYear.objects.get(currentYear = 1)
    curUser = User.objects.select_related('trafficDuty_User','linkedUser','linkedUser__linkedUserAccount__volunteerhours_set','linkedUser__linkedUserAccount__rewardCardValue')\
        .prefetch_related('linkedUser__linkedUserAccount__family').get(pk=request.user.id)
    rewardCardData = curUser.rewardCardValue.filter(schoolYear = curYear).order_by('-refillDate')
    volhours = curUser.volunteerhours_set.select_related('event','family').filter(schoolYear=curYear).all().order_by('-eventDate')
    traffic = curUser.trafficDuty_User.filter(schoolYear = curYear).order_by('-weekStart')
    rewardCardSum =curUser.rewardCardValue.filter(schoolYear = curYear).aggregate(Sum('volunteerHours')).values()[0]
    parkingDutySum=traffic.aggregate(Sum('volunteerHours')).values()[0]
    volunteerHoursSum=volhours.filter(approved=True).aggregate(Sum('volunteerHours')).values()[0]
    if rewardCardSum==None:
        rewardCardSum=0
    if volunteerHoursSum ==None:
        volunteerHoursSum = 0
    if parkingDutySum==None:
        parkingDutySum=0
    totalVolunteerHoursUser = rewardCardSum+volunteerHoursSum+parkingDutySum
    hasInterests = curUser.linkedUser.interest.count()
    if curUser.family.count()>1:
        multFam = True
    else:
        multFam = False

    response = render(request, 'volunteerData/volunteerData.html',{'rewardCardData':rewardCardData,
         'volHours':volhours,'rewardCardSum':rewardCardSum,'volunteerHoursSum':volunteerHoursSum,
        'totalVolunteerHoursUser':totalVolunteerHoursUser,'multFam':multFam,
        'curYear':curYear,'curUser':curUser,'hasInterests':hasInterests,'traffic':traffic})
    return response



@login_required
def userSettings(request):
    #profile = VolunteerProfile.objects.get_or_create(linkedUserAccount = request.user)
    #cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get_or_create(linkedUserAccount= auth)
    cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType').prefetch_related('interest').get(linkedUserAccount= request.user)
    userFamily = FamilyProfile.objects.filter(famvolunteers = request.user).all()
    rewardCards = RewardCardUsers.objects.filter(linkedUser=request.user).all()
    if request.session.get('teachUpdate'):
        del request.session['teachUpdate']
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
        return reverse('familyprofile', kwargs={'famid': self.kwargs['famId']})

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


def StudentIndex(request):
    '''
    This view populates the volunteerIndex table with all active users
    '''
    StudentIndex = Student.objects.all().select_related('grade').prefetch_related('familyprofile_set','teacher').filter(activeStatus=True)
    response = render(request, 'tables/StudentIndex.html',{'StudentIndex':StudentIndex})
    return response


class UpdateStudent(LoginRequiredMixin,UpdateView):
    form_class = StudentUpdateForm
    template_name = 'forms/studentUpdate.html'

    def get_object(self):
        return Student.objects.get(pk=self.kwargs['stuId'])

    def get_success_url(self):
        if self.request.session.get('teachUpdate'):
            teachid= self.request.session['teachUpdate']
            return reverse('teacherProfile', kwargs={'teachid':teachid})
        else:
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
        context['dataList']=VolunteerHours.objects.filter(volunteer=self.request.user).filter(schoolYear=SchoolYear.objects.get(currentYear=1)).order_by('-dateUpdated')
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

            for fam in ur.linkedUserAccount.family.all():
                if fam.active:
                    FamilyAggHours.objects.get_or_create(family = fam, schoolYear = SchoolYear.objects.get(currentYear=1))
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


def get_tasks(request,eventid):
    print eventid
    if request.is_ajax():
        q = request.GET.get('term', '')
        tasks = EventTasks.objects.filter(relatedEvent=eventid).filter(taskName__icontains = q )[:20]
        print tasks
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


def ApproveHoursCheckBox(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        rec = VolunteerHours.objects.get(pk=vol)
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


class addNewInterest(LoginRequiredMixin, CreateView):
    form_class = AddInterestForm
    template_name = 'forms/addInterests.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'interestIndex'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'addNewInterest'
        return reverse(retPage)

    def form_valid(self, form):
        return super(addNewInterest,self).form_valid(form)

class UpdateInterest(LoginRequiredMixin,UpdateView):
    form_class = AddInterestForm
    template_name = 'forms/addInterests.html'

    def get_object(self):
        return VolunteerInterests.objects.get(interestId=self.kwargs['intid'])

    def get_success_url(self):
        return reverse('interestIndex')


def markInterestAsInactive(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerInterests.objects.get(pk=vol)
        ur.active = False
        ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def markInterestAsActive(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerInterests.objects.get(pk=vol)
        ur.active = True
        ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def deleteInterest(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = VolunteerInterests.objects.get(pk=vol).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


import django_filters
class RecruitingFilter(django_filters.FilterSet):
    family__students__grade = django_filters.ModelMultipleChoiceFilter(queryset=GradeLevel.objects.all())
    family__students__teacher = django_filters.ModelMultipleChoiceFilter(queryset=Teachers.objects.all())
    family__familyAgg__totalVolHours__gt = django_filters.NumberFilter(name='family__familyAgg__totalVolHours',lookup_type='gte',label='Total Family hours (min)')
    family__familyAgg__totalVolHours__lt = django_filters.NumberFilter(name='family__familyAgg__totalVolHours', lookup_type='lte',label='Total Family hours (max)')
    family__familyAgg__trafficDutyCount__gt = django_filters.NumberFilter(name='family__familyAgg__trafficDutyCount', lookup_type='gte',label='Traffic Duty (min)')
    family__familyAgg__trafficDutyCount__lt = django_filters.NumberFilter(name='family__familyAgg__trafficDutyCount', lookup_type='lte',label='Traffic Duty (max)')
    class Meta:
        model = User
        fields =['linkedUser__interest',
                 'family__students__grade','family__students__teacher']


@login_required
def recruiting_list(request):
    f = RecruitingFilter(request.GET, queryset=User.objects.filter(is_active=True).filter(linkedUser__doNotEmail=False).all())
    lx = User.objects.prefetch_related('family','family__familyAgg','family__familyAgg__schoolYear').filter(pk__in=f.qs)\
        .values('name','email','id','family__familyName',
               'family__familyAgg__totalVolHours','family__familyAgg__trafficDutyCount',
               'family__familyAgg__schoolYear__currentYear')

    #apply additional filter logic

    #apply greater than logic to remove dupes for total volunteer hours
    if request.GET:
        if request.GET['family__familyAgg__totalVolHours__gt']:
            lx1=[]
            for p in lx:
                if p['family__familyAgg__totalVolHours']>=float(request.GET['family__familyAgg__totalVolHours__gt']):
                    lx1.append(p)
            lx = lx1

        #apply less than logic to remove dupes for total volunteer hours
        if request.GET['family__familyAgg__totalVolHours__lt']:
            lx1=[]
            for p in lx:
                if p['family__familyAgg__totalVolHours']<=float(request.GET['family__familyAgg__totalVolHours__lt']):
                    lx1.append(p)
            lx = lx1

        #apply greater than logic to remove dupes for total traffic duty
        if request.GET['family__familyAgg__trafficDutyCount__gt']:
            lx1=[]
            for p in lx:
                if p['family__familyAgg__trafficDutyCount']>=float(request.GET['family__familyAgg__trafficDutyCount__gt']):
                    lx1.append(p)
            lx = lx1

        #apply less than logic to remove dupes for total volunteer hours
        if request.GET['family__familyAgg__trafficDutyCount__lt']:
            lx1=[]
            for p in lx:
                if p['family__familyAgg__trafficDutyCount']<=float(request.GET['family__familyAgg__trafficDutyCount__lt']):
                    lx1.append(p)
            lx = lx1

        lx1 = []
        for p in lx:
            if p['family__familyAgg__schoolYear__currentYear']==1:
                lx1.append(p)
        lx=lx1
    #lx= f.queryset.filter(family__familyAgg__schoolYear=SchoolYear.objects.
                          #get(currentYear=1)).values('name','family','family__familyAgg__totalVolHours')
    request.session['filterPath']= request.get_full_path()
    return render(request, 'tables/recruiting.html',{'filter':f,'lx':lx})


def get_recruits_email(request):
    selected_values = request.POST.getlist('UserRecs')
    email_list=[]
    for vol in selected_values:
        email_list.append(vol)
    email_list.append(request.user.email)
    request.session['recruitingEmailList']=list(set(email_list))
    print request.session['recruitingEmailList']
    return HttpResponseRedirect(reverse('sendRecruitingEmail'))

'''
def send_recruiting_email(request):
    if request.method=='POST':
        emailForm = RecruitingEmailForm(request.POST or None, request.FILES or None)
        if emailForm.is_valid():
            subject = request.POST['subject']
            msgbody = request.POST['msgbody']
            if 'file' in request.FILES:
                attach = request.FILES['file']
            destination = set(request.session['recruitingEmailList'])
            destination= list(destination)
            html_content = (subject,msgbody)
            msg = EmailMessage(subject,msgbody,'NSA-VolunteerRecruiting@nsavms.com',bcc=destination, headers = {'Reply-To': 'volunteer@nstaracademy.org'})
            if 'file' in request.FILES:
                msg.attach(attach.name,attach.read(),attach.content_type)
            msg.send()
            return HttpResponseRedirect(request.session['filterPath'])

    else:
        volunteerNames = User.objects.filter(email__in=request.session['recruitingEmailList']).values('name')
        emailForm = RecruitingEmailForm()
    ctx={'form':emailForm, 'text_dc':file, 'recps':request.session['recruitingEmailList'],'volNames':volunteerNames}
    return render_to_response('forms/recruitingEmailForm.html', ctx, context_instance=RequestContext(request))
'''
def send_recruiting_email(request):
    volunteerNames = User.objects.filter(email__in=request.session['recruitingEmailList']).values('name')
    if request.method=='POST':
        emailForm = RecruitingEmailForm(request.POST or None, request.FILES or None)
        if emailForm.is_valid():
            print emailForm.is_valid()
            subject = request.POST['subject']
            msgbody = request.POST['msgbody']
            if 'file' in request.FILES:
                attach = request.FILES['file']
            destination = set(request.session['recruitingEmailList'])
            destination= list(destination)
            if 'file' in request.FILES:
                requests.post(
                    "https://api.mailgun.net/v3/mg.nsavms.com/messages",
                    auth=("api", settings.MAILGUN_API_KEY),
                      files=[('attachment',attach)],
                      data={"from": '"NSA-VolunteerRecruiting" <volunteer@nstaracademy.org>',
                      "to":["volunteer@nstaracademy.org"],
                      "bcc": destination,
                      "subject": subject,
                      "text": msgbody,
                      "o:tracking": True})
            else:
                requests.post(
                    "https://api.mailgun.net/v3/mg.nsavms.com/messages",
                    auth=("api", settings.MAILGUN_API_KEY),
                      data={"from": '"NSA-VolunteerRecruiting" <volunteer@nstaracademy.org>',
                      "to":["volunteer@nstaracademy.org"],
                      "bcc": destination,
                      "subject": subject,
                      "text": msgbody,
                      "o:tracking": True})
            return HttpResponseRedirect(request.session['filterPath'])

    else:
        emailForm = RecruitingEmailForm()
    ctx={'form':emailForm, 'text_dc':file, 'recps':request.session['recruitingEmailList'],'volNames':volunteerNames}
    return render_to_response('forms/recruitingEmailForm.html', ctx, context_instance=RequestContext(request))

def decline_volunteerHours_email(request,vhoursId):
    rec = VolunteerHours.objects.get(pk=vhoursId)
    if request.method=='POST':
        emailForm = DeclineLoggedHours(request.POST or None)
        if emailForm.is_valid():
            subject = request.POST['subject']
            msgbody = request.POST['msgbody']
            destination = rec.volunteer.email
            approver = request.user.email
            html_content = (subject,msgbody)
            msg = EmailMessage(subject,msgbody,'NSA-VolunteerRecruiting@nsavms.com',to=[destination],bcc=[approver], headers = {'Reply-To': 'volunteer@nstaracademy.org'})
            msg.send()
            rec.delete()
            return HttpResponseRedirect(reverse('approveHours'))

    else:
        volunteerNames = list(rec.volunteer.name)
        emailForm = DeclineLoggedHours()
    ctx={'form':emailForm, 'recps':rec.volunteer.name,'volNames':volunteerNames,'volDetail':rec}
    return render_to_response('forms/decliningVolunteerHours.html', ctx, context_instance=RequestContext(request))



def massPasswordReset(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        volunteer = User.objects.get(pk = VolunteerProfile.objects.get(pk=vol).linkedUserAccount_id)
        password = User.objects.make_random_password(8)
        volunteer.set_password(password)
        volunteer.save()
        body = """
            Below is your username and new password for the North Star Academy VMS site:
            Username:{username}
            Password:{password}
            You can login here:http://www.nsavms.com/login/
            Change your password here:http://www.nsavms.com/changePassword/
            """.format(username = volunteer.email, password=password)

        email = EmailMessage(
                '[NSA VMS] Password Reset', body, 'no-reply@nsavms.com',
                [volunteer.email])
        email.send()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class UpdateVolunteerLogin(LoginRequiredMixin,UpdateView):
    form_class = EditVolunteersLogin
    template_name = 'forms/addNewUserToFamily.html'

    def get_object(self):
        return User.objects.get(pk=self.kwargs['volid'])
        #return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        return reverse('volunteerIndex')

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateVolunteerLogin, self).get_context_data(*args, **kwargs)
        context['isEdit'] = 'Edit'
        return context

    def form_valid(self, form):
        usr = User.objects.get(pk=self.kwargs['volid'])
        form.instance.last_login =usr.last_login
        form.instance.password =usr.password
        form.instance.date_joined =usr.date_joined

        profile = VolunteerProfile.objects.get(pk=usr.linkedUser.volunteerProfileID)
        profile.firstName = form.instance.name.split(' ',1)[0]
        profile.lastName = form.instance.name.split(' ',1)[1]
        profile.save()
        return super(UpdateVolunteerLogin,self).form_valid(form)


class addNewTraffic_weekly(LoginRequiredMixin, CreateView):
    form_class = TrafficWeeklyUpdate
    template_name = 'forms/trafficWeekly.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'trafficReportWeekly'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'addWeeklyTraffic'
        return reverse(retPage)




class editTraffic_weekly(LoginRequiredMixin,UpdateView):
    form_class = TrafficWeeklyUpdate
    template_name = 'forms/trafficWeekly.html'

    def get_object(self):
        return Traffic_Duty.objects.get(trafficDutyId=self.kwargs['trafficid'])

    def get_context_data(self, *args, **kwargs):
        context = super(editTraffic_weekly, self).get_context_data(*args, **kwargs)
        context['isEdit'] = 'Edit'
        return context

    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'trafficReportWeekly'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'addWeeklyTraffic'
        return reverse(retPage)




class TrafficReportWeekly(TemplateView):

    template_name = "tables/trafficDutyWeekly.html"

    def get_context_data(self, **kwargs):
        context = super(TrafficReportWeekly, self).get_context_data(**kwargs)
        context['recentTraffic'] = Traffic_Duty.objects.all().order_by('-dateCreated')
        return context

def deleteTrafficDuty(request, trafficid):
    obj = Traffic_Duty.objects.get(pk=trafficid)
    obj.delete()
    return HttpResponseRedirect(reverse('trafficReportWeekly'))


def RewardCardUserIndex(request):
    '''
    This view populates the volunteerIndex table with all active users
    '''
    volunteerIndex = RewardCardUsers.objects.select_related('linkedUser','linkedUser__linkedUser').prefetch_related('family').all().order_by('linkedUser__linkedUser__lastName')
    response = render(request, 'tables/rewardCardUserIndex.html',{'volunteerIndex':volunteerIndex})
    return response


class AddRewardCardUsersView(FormView):
    template_name = 'forms/RewardCardUsers.html'
    form_class = upLoadRewardCardUsers
    #success_url = '/upload/'

    def get_success_url(self):
        return reverse('volunteerIndex')

    def form_valid(self, form):
        form.process_data()
        return super(AddRewardCardUsersView, self).form_valid(form)

class AddRewardCardPurchaseData(FormView):
    template_name = 'forms/RewardCardUsers.html'
    form_class = upLoadRewardCardPurchaseData
    #success_url = '/upload/'

    def get_success_url(self):
        return reverse('volunteerIndex')

    def form_valid(self, form):
        form.process_data()
        return super(AddRewardCardPurchaseData, self).form_valid(form)





def GetMailGunLogs():
    logData=[]
    myDate = datetime.datetime.now() - datetime.timedelta(days=10)
    startDate = myDate.strftime('%a, %d %B %y %H:%M:%S -0000')
    mgreturn= requests.get(
        "https://api.mailgun.net/v3/mg.nsavms.com/events",
        auth=("api", settings.MAILGUN_API_KEY),
        params={"begin"       : startDate,
                "ascending"   : "yes",
                "limit"       :  300,
                "pretty"      : "yes"
                })
    parsed_json = json.loads(mgreturn.text)
    for y in parsed_json['items']:
        mgDict={}
        mgDict['recipient'] = y['recipient']
        mgDict['date'] = datetime.datetime.fromtimestamp(y['timestamp'])
        mgDict['subject']=y['message']['headers']['subject']
        mgDict['event']=y['event']
        mgDict['timestamp']=y['timestamp']
        logData.append(mgDict)
        newlist = sorted(logData, key=itemgetter('date'), reverse=True)
    return newlist


def GetMailGunSuppressions():
    logData=[]
    mgreturn = requests.get(
        "https://api.mailgun.net/v3/mg.nsavms.com/bounces",
        auth=("api", settings.MAILGUN_API_KEY))
    parsed_json = json.loads(mgreturn.text)
    for y in parsed_json['items']:
        mgDict={}
        mgDict['recipient'] = y['address']
        mgDict['date'] = y['created_at']
        mgDict['error']=y['error']
        logData.append(mgDict)

    return logData

def mailGunLog(request):
    logData = GetMailGunLogs()
    suppressions = GetMailGunSuppressions()
    return render_to_response('tables/mailResponses.html',{'logdata':logData, 'suppressions':suppressions})