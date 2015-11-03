from django.shortcuts import render,get_object_or_404, render_to_response
from django.views.generic import FormView, TemplateView, RedirectView, UpdateView
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from forms import LoginForm, UserProfileForm,FamilyProfileForm, AddNewFamily

from .models import *
from authtools.models import User
from django.forms.formsets import formset_factory


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


def homeView(request):
    news = VolunteerNews.objects.all()
    response = render(request,'news.html',{'news':news})
    return response

def userVolunteerData(request):
    '''
    This view will generate all data needed for all user data. This will include family,
    grocery & donotions data
    '''
    #news = VolunteerNews.objects.all()
    response = render(request,'volunteerData/volunteerData.html')
    #response = TemplateResponse(request, 'news.html', {})
    # Register the callback
    # Return the response
    return response

def VolunteerOpportunities(request):
    #news = VolunteerNews.objects.all()
    response = render(request,'volunteerOpportunities.html')
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

def InterestList(request):
    '''
    View for active Interests list.
    Users can add interests from this template
    '''
    if request.user.is_authenticated():
        profileInt = VolunteerProfile.objects.get(linkedUserAccount=request.user).interest.all()
    else:
        profileInt =''
    interests = VolunteerInterests.objects.filter(active=True).all()
    response = render(request,'volunteerInterests.html',{'interests':interests,'profileInt':profileInt})
    return response

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
