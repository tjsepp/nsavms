from django.shortcuts import render,get_object_or_404, render_to_response, redirect
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
from django.db.models import Sum
from nsaSchool.models import VolunteerNews, SchoolYear
from authtools.forms import UserCreationForm

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



class VolunteerIndex(ListView):
    model = VolunteerProfile
    paginate_by = 100
    queryset = VolunteerProfile.objects.all().order_by('lastName')
    context_object_name = "volunteerIndex"
    template_name = "tables/volunteerIndex.html"

class FamilyIndex(ListView):
    model = FamilyProfile
    paginate_by = 100
    queryset = FamilyProfile.objects.all().order_by('familyName')
    context_object_name = "FamilyIndex"
    template_name = "tables/FamilyIndex.html"


@login_required
def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''

    curYear = SchoolYear.objects.get(currentYear = 1)
    curUser = User.objects.select_related('volunteerhours_set','rewardCardValue','family','linkedUser').get(pk=request.user.id)
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
    cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get(linkedUserAccount= request.user)
    userFamily = FamilyProfile.objects.filter(famvolunteers = request.user).all()
    rewardCards = RewardCardUsers.objects.filter(linkedUser=request.user).all()
    response = render(request, 'userprofile/userprofile.html',{'cur_user':cur_user,'userFamily':userFamily,'rewardCards':rewardCards})
    return response



class UpdateVolunteerProfile(LoginRequiredMixin,UpdateView):
    form_class = UserProfileForm
    template_name = 'forms/updateVolunteerProfile.html'

    def get_object(self):
        return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
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
        return reverse('userVolunteerData')

    def get_initial(self):
        return {
            'volunteer':self.request.user
        }

    def form_valid(self, form):
        form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
        form.save()
        return super(logUserHours,self).form_valid(form)

    def get_context_data(self,*args, **kwargs):
        context = super(logUserHours,self).get_context_data(*args, **kwargs)
        context['schoolYear'] = SchoolYear.objects.get(currentYear=1)
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
        form.save()
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
        return reverse('userVolunteerData')



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
    template_name = 'forms/static/js/addNewFamily.html'
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
            message="Thank You!"
            for form in formset:
                form.save()
                family.famvolunteers.add(form.instance)
                family.save()
            return HttpResponseRedirect(reverse_lazy('volunteerIndex'))
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


def RemoveContactFromFamily(request,famid,volunteerid):
    family = FamilyProfile.objects.get(pk= famid)
    volunteer = User.objects.get(pk = volunteerid)
    family.famvolunteers.remove(volunteer)
    family.save()
    return HttpResponseRedirect(reverse('familyprofile', kwargs={'famid': famid}))



def AddTrafficVolunteers(request):
    addVolunteerFormset = formset_factory(AddTrafficVolunteersForm, extra=10)
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
