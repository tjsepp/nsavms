from django.shortcuts import render
from django.views.generic import FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout





class LogoutView(RedirectView):
    permanent = False
    url = reverse_lazy('user_dashboard')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView,self).get(request,args,kwargs)