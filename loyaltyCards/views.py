from django.shortcuts import render,get_object_or_404, render_to_response, redirect
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, \
        ListView, DeleteView,TemplateView
import json
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.template import RequestContext
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from .models import *
from .forms import *
from nsavolunteer.models import FamilyProfile
# Create your views here.


class addLoyaltyCardNumber(LoginRequiredMixin, CreateView):
    form_class = AddLoyaltyCardNumberForm
    template_name = 'forms/addLoyaltyCard.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            famId = FamilyProfile.objects.filter(famvolunteers = self.request.user)[0].familyProfileId
            print 'family should be below'
            print famId
            return reverse('familyprofile', kwargs={'famid':famId})
        elif self.request.POST.get('saveAndAdd'):
            return reverse('addNewLoyaltyCard')

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(addLoyaltyCardNumber, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = self.request.user)
        kwargs['user'] = self.request.user
        return kwargs