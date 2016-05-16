from django.shortcuts import render,get_object_or_404, render_to_response, redirect
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, \
        ListView, DeleteView,TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.template import RequestContext
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from .models import *
from .forms import *


class addVolunteerEvent(LoginRequiredMixin, CreateView):
    form_class = EventsForm
    template_name = 'forms/addEditEvent.html'

    def get_success_url(self):
        return reverse('home')
