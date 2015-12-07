from django.shortcuts import render,get_object_or_404, render_to_response
from django.views.generic import FormView, TemplateView, RedirectView, UpdateView
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.template import RequestContext
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from forms import LoginForm, UserProfileForm,FamilyProfileForm, AddNewFamily, PasswordChangeFormExtra
from .models import *
from authtools.models import User
from django.forms.formsets import formset_factory
from django.db.models import Sum
from nsaSchool.models import VolunteerNews, SchoolYear


def homeView(request):
    news = VolunteerNews.objects.all()
    response = render(request,'home.html')
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



def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''

    curYear = SchoolYear.objects.get(currentYear = 1)
    rewardCardData = RewardCardUsage.objects.filter(volunteerId = request.user).filter(schoolYear = curYear)
    totalVolunteerHoursUser =RewardCardUsage.objects.filter(volunteerId =
        request.user).filter(schoolYear = curYear).aggregate(Sum('volunteerHours')).values()[0]

    response = render(request,'volunteerData/volunteerData.html',{'rewardCardData':rewardCardData,
        'totalVolunteerHoursUser':totalVolunteerHoursUser})
    #response = TemplateResponse(request, 'news.html', {})
    # Register the callback
    # Return the response
    return response



def userSettings(request):
    #profile = VolunteerProfile.objects.get_or_create(linkedUserAccount = request.user)
    #cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get_or_create(linkedUserAccount= auth)
    cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get(linkedUserAccount= request.user)
    userFamily = VolunteerToFamily.objects.select_related('group').filter(person_id = request.user).all()
    response = render(request,'userprofile/userProfile.html',{'cur_user':cur_user,'userFamily':userFamily})
    return response


class UpdateVolunteerProfile(UpdateView):
    form_class = UserProfileForm
    template_name = 'forms/updateVolunteerProfile.html'

    def get_object(self):
        return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        return reverse('user_dashboard')

    def get_context_data(self, **kwargs):
        context = super(UpdateVolunteerProfile, self).get_context_data(**kwargs)
        context['interests'] = VolunteerInterests.objects.filter(active=True).all()
        context['profileInt'] = self.object.interest.all()
        return context


class UpdateFamilyProfile(UpdateView):
    form_class = FamilyProfileForm
    template_name = 'forms/updateFamilyProfile.html'

    def get_object(self):
        return FamilyProfile.objects.get(pk=self.kwargs['famId'])
        #return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        return reverse('user_dashboard')

    '''
    def get_context_data(self, *args, **kwargs):
        context = super(UpdateVolunteerProfile, self).get_context_data(*args, **kwargs)
        context['fullName'] = VolunteerProfile.objects.get(linkedUserAccount=self.request.user).fullName
        return context
    '''

    def form_valid(self, form):
        profile = VolunteerProfile.objects.get(linkedUserAccount=self.request.user)
        userAcct =User.objects.get(pk=self.request.user.id)
        profile.linkedUserAccount_id = self.request.user
        userAcct.name ='%s %s' %(form.instance.firstName,form.instance.lastName)
        userAcct.save()
        return super(UpdateVolunteerProfile, self).form_valid(form)

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

def familyFormset(request):
    familyFormset = formset_factory(AddNewFamily, extra=4)
    return render_to_response('forms/familyFormset.html',{'formset':familyFormset},context_instance=RequestContext(request))
