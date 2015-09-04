from django.shortcuts import render,get_object_or_404
from django.views.generic import FormView, TemplateView, RedirectView, UpdateView
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.response import TemplateResponse
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from forms import LoginForm, UserProfileForm
from .models import *
from authtools.models import User



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
    #response = TemplateResponse(request, 'news.html', {})
    # Register the callback
    # Return the response
    return response

def userVolunteerData(request):
    news = VolunteerNews.objects.all()
    response = render(request,'volunteerData/volunteerData.html')
    #response = TemplateResponse(request, 'news.html', {})
    # Register the callback
    # Return the response
    return response


def userSettings(request):
    cur_user = VolunteerProfile.objects.select_related('linkedUserAccount','volunteerType','interest').get(linkedUserAccount= request.user)
    response = render(request,'userprofile/userProfile.html',{'cur_user':cur_user})
    return response


class UpdateVolunteerProfile(UpdateView):
    form_class = UserProfileForm
    template_name = 'forms/updateVolunteerProfile.html'

    def get_object(self):
        return VolunteerProfile.objects.get(linkedUserAccount=self.request.user)

    def get_success_url(self):
        return reverse('user_dashboard')


    def get_context_data(self, *args, **kwargs):
        context = super(UpdateVolunteerProfile, self).get_context_data(*args, **kwargs)
        context['fullName'] = VolunteerProfile.objects.get(linkedUserAccount=self.request.user).fullName
        return context


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