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


class addVolunteerEvent(LoginRequiredMixin, CreateView):
    form_class = EventsForm
    template_name = 'forms/addEditEvent.html'

    def get_success_url(self):
        return reverse('eventIndex')

class updateVolunteerEvent(LoginRequiredMixin,UpdateView):
    form_class = EventsForm
    template_name = 'forms/addEditEvent.html'

    def get_object(self, queryset=None):
        return NsaEvents.objects.get(pk=self.kwargs['eventID'])

    def form_valid(self, form):
        form.save()
        return super(updateVolunteerEvent,self).form_valid(form)

    def get_success_url(self):
        return reverse('eventIndex')

def EventIndex(request):
    EventIndex = NsaEvents.objects.all().prefetch_related('eventLeader')
    response = render(request, 'tables/eventsList.html',{'EventIndex':EventIndex})
    return response


#def makeEventsViewable(request):
#    selected_values = request.POST.getlist('UserRecs')
#    for vol in selected_values:
#        ur = VolunteerProfile.objects.get(pk=vol)
#        if ur.linkedUserAccount.is_active==False:
#            ur.linkedUserAccount.is_active = True
#            ur.linkedUserAccount.save()
#    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




class LogHoursFromEvent(LoginRequiredMixin, CreateView):
    form_class = LogHoursFromEventForm
    template_name = 'forms/LogHoursFromEvent.html'


    def get_success_url(self):
        if self.request.POST.get('save'):
             retPage = 'home'
        elif self.request.POST.get('saveAndAdd'):
             retPage = "'log_hours_from_event',kwargs={'eventId': %s}" % (str(self.kwargs['eventId']))
        return reverse('log_hours_from_event', kwargs={'eventId':self.kwargs['eventId']})
        #return reverse(retPage)

    def get_initial(self):
        return {
            'event':self.kwargs['eventId']

        }

    def form_valid(self, form):
        form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
        form.instance.eventId=self.kwargs['eventId']
        #form.save()
        return super(LogHoursFromEvent,self).form_valid(form)

    def get_context_data(self,*args, **kwargs):
        context = super(LogHoursFromEvent,self).get_context_data(*args, **kwargs)
        context['schoolYear'] = SchoolYear.objects.get(currentYear=1)
        context['eventName']=NsaEvents.objects.get(pk=self.kwargs['eventId']).eventName
        context['tasks'] = ', '.join("'{0}'".format(x[0]) for x in EventTasks.objects.all().values_list('taskName'))
        return context

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(LogHoursFromEvent, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = self.request.user)
        kwargs['user'] = self.request.user
        return kwargs

def get_related_families(request,usid):
    relatedUser = usid
    #print 'ajax user name',relatedUser

    result_set=[]
    all_families =[]
    #relatedFamilies = str(relatedUser[1:-1])
    selected_user=FamilyProfile.objects.filter(famvolunteers=relatedUser)
    #print 'selected user', relatedUser
    all_families = selected_user.all()
    for family in all_families:
        result_set.append({family.familyProfileId:family.familyName})
    return HttpResponse(json.dumps(result_set), content_type='application/json')

