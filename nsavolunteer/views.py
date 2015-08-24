from django.shortcuts import render
from django.views.generic import FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.template.response import TemplateResponse
from django.contrib.auth.forms import AuthenticationForm
from forms import LoginForm

def homeView(request):
    # Create a response
    response = TemplateResponse(request, 'account/base.html', {})
    # Register the callback
    # Return the response
    return response

class LoginView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('user_dashboard')

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user )
        return super(LoginView, self).form_valid(form)


class LogoutView(RedirectView):
    permanent = False
    url = reverse_lazy('user_dashboard')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView,self).get(request,args,kwargs)