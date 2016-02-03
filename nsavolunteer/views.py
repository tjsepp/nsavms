from django.shortcuts import render,get_object_or_404, render_to_response
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, ListView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.template import RequestContext
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from forms import LoginForm, UserProfileForm,FamilyProfileForm,PasswordChangeFormExtra, StudentUpdateForm, AddUserEventForm,AddNewFamily,AddFamilyVolunteers
from .models import *
from django.forms.formsets import formset_factory
from django.db.models import Sum
from nsaSchool.models import VolunteerNews, SchoolYear
from authtools.forms import UserCreationForm


def homeView(request):
    news = VolunteerNews.objects.all()
    response = render(request, 'home.html')
    return response


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

@login_required
def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''

    curYear = SchoolYear.objects.get(currentYear = 1)
    curUser = User.objects.select_related('volunteerhours_set','rewardCardValue','family').get(pk=request.user.id)
    rewardCardData = curUser.rewardCardValue.filter(schoolYear = curYear).order_by('-refillDate')
    volhours = curUser.volunteerhours_set.select_related('event').filter(schoolYear=curYear).all().order_by('-eventDate')
    rewardCardSum =curUser.rewardCardValue.filter(schoolYear = curYear).aggregate(Sum('volunteerHours')).values()[0]
    volunteerHoursSum=volhours.aggregate(Sum('volunteerHours')).values()[0]
    if rewardCardSum==None:
        rewardCardSum=0
    if volunteerHoursSum ==None:
        volunteerHoursSum = 0
    familySums = curUser.volunteerhours_set.values('family__familyName').annotate(total=Sum('volunteerHours')).order_by('family')
    totalVolunteerHoursUser = rewardCardSum+volunteerHoursSum
    response = render(request, 'volunteerData/volunteerData.html',{'rewardCardData':rewardCardData,
         'volHours':volhours,'rewardCardSum':rewardCardSum,'volunteerHoursSum':volunteerHoursSum,
        'familySums':familySums,'totalVolunteerHoursUser':totalVolunteerHoursUser,
        'curYear':curYear,'curUser':curUser})
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
    family = FamilyProfile.objects.prefetch_related('famvolunteers','famvolunteers__linkedUser').get(pk=famid)

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