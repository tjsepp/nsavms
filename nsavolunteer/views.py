from django.shortcuts import render
from django.views.generic import FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.response import TemplateResponse
from django.contrib.auth.forms import AuthenticationForm
from forms import LoginForm
from .models import *

def homeView(request):
    news = VolunteerNews.objects.all()
    response = render(request,'news.html',{'news':news})
    #response = TemplateResponse(request, 'news.html', {})
    # Register the callback
    # Return the response
    return response

class LoginView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

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

def userSettings(request):
    cur_user = VolunteerProfile.objects.select_related('user').get(linkedUserAccount= request.user)
    response = render(request,'userprofile/userProfile.html',{'cur_user':cur_user})
    return response

'''
def UserClientList(request):
    ac = AcMember.objects.get(user__username=request.user)
    accountlist = ac.acmember.all()
    response = render(request,'userClientList.html',{'accountlist':accountlist})
    return response
'''