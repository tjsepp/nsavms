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
from nsavolunteer.models import VolunteerHours


class addVolunteerEvent(LoginRequiredMixin, CreateView):
    form_class = EventsForm
    template_name = 'forms/addEditEvent.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            return reverse('eventIndex')
        elif self.request.POST.get('saveAndAdd'):
            return reverse('addVolunteerEvent')

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


def EventTaskIndex(request):
    TaskIndex = EventTasks.objects.all().select_related('task_to_event')
    response = render(request, 'tables/eventTaskList.html',{'TaskIndex':TaskIndex})
    return response


class addVolunteerEventTask(LoginRequiredMixin, CreateView):
    form_class = EventTasksForm
    template_name = 'forms/addEditEventTask.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            return reverse('taskIndex')
        elif self.request.POST.get('saveAndAdd'):
            return reverse('addVolunteerEventTask')

class updateVolunteerEventTask(LoginRequiredMixin,UpdateView):
    form_class = EventTasksForm
    template_name = 'forms/addEditEventTask.html'

    def get_object(self, queryset=None):
        return EventTasks.objects.get(pk=self.kwargs['taskID'])

    def form_valid(self, form):
        form.save()
        return super(updateVolunteerEventTask,self).form_valid(form)

    def get_success_url(self):
        return reverse('taskIndex')


class LogHoursFromEvent(LoginRequiredMixin, CreateView):
    form_class = LogHoursFromEventForm
    template_name = 'forms/LogHoursFromEvent.html'


    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'home'
            return reverse('log_hours_from_event', kwargs={'eventId':self.kwargs['eventId']})
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
        form.instance.approved = True
        form.save()
        return super(LogHoursFromEvent,self).form_valid(form)

    def get_context_data(self,*args, **kwargs):
        context = super(LogHoursFromEvent,self).get_context_data(*args, **kwargs)
        context['schoolYear'] = SchoolYear.objects.get(currentYear=1)
        context['eventName']=NsaEvents.objects.get(pk=self.kwargs['eventId']).eventName
        context['eventid']=self.kwargs['eventId']
        context['tasks'] = ', '.join("'{0}'".format(x[0]) for x in EventTasks.objects.all().values_list('taskName'))
        context['dataList']=VolunteerHours.objects.filter(event=self.kwargs['eventId']).filter(schoolYear=SchoolYear.objects.get(currentYear=1)).order_by('-dateUpdated')
        return context

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(LogHoursFromEvent, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = self.request.user)
        kwargs['user'] = self.request.user
        return kwargs


class UpdateLoggedHoursFromEvent(LoginRequiredMixin,UpdateView):
    form_class = LogHoursFromEventForm
    template_name = 'forms/LogHoursFromEvent.html'

    def get_object(self, queryset=None):
        return VolunteerHours.objects.select_related('family','schoolYear','volunteer__linkedUser__user').get(pk=self.kwargs['vhoursID'])

    def get_context_data(self,*args, **kwargs):
        context = super(UpdateLoggedHoursFromEvent,self).get_context_data(*args, **kwargs)
        rec = self.get_object()
        context['schoolYear'] = rec.schoolYear#SchoolYear.objects.get(currentYear=1)
        context['eventName']=rec.event.eventName#self.event.eventName
        context['eventid']=rec.event.eventId#self.event.eventId
        context['isEdit'] = True
        context['tasks'] = ', '.join("'{0}'".format(x[0]) for x in EventTasks.objects.all().values_list('taskName'))
        context['dataList']=VolunteerHours.objects.select_related('family','schoolYear').filter(event=rec.event.eventId).filter(schoolYear=SchoolYear.objects.get(currentYear=1)).order_by('-dateUpdated')
        #context['dataList']=VolunteerHours.objects.filter(volunteer=rec.volunteer).filter(schoolYear=SchoolYear.objects.get(currentYear=1)).order_by('-dateUpdated')

        return context

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        rec = self.get_object()
        kwargs = super(UpdateLoggedHoursFromEvent, self).get_form_kwargs()
        kwargs['famcount'] = FamilyProfile.objects.filter(famvolunteers = rec.volunteer)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.schoolYear = SchoolYear.objects.get(currentYear=1)
        form.instance.eventId=self.kwargs['eventId']
        form.instance.approved = True
        form.save()
        return super(UpdateLoggedHoursFromEvent,self).form_valid(form)

    def get_success_url(self):
        rec = self.get_object()
        if self.request.POST.get('save'):
            retPage = 'home'
            return reverse('edit_hours_from_event', kwargs={'vhoursID':self.kwargs['vhoursID']})
        elif self.request.POST.get('saveAndAdd'):
            retPage = "'log_hours_from_event',kwargs={'eventId': %s}" % (str(rec.event.eventId))
            return reverse('log_hours_from_event', kwargs={'eventId':rec.event.eventId})

def deleteLoggedHoursfromevent(request, vhoursID):
    obj = VolunteerHours.objects.get(pk=vhoursID)
    obj.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



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

