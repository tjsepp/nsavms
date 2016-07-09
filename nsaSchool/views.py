from django.shortcuts import render
from models import Teachers
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, \
        ListView, DeleteView,TemplateView
from braces.views import LoginRequiredMixin
from forms import AddNewTeacherForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def TeacherIndex(request):
    teacherIndex = Teachers.objects.all()
    response = render(request, 'tables/teacherIndex.html',{'teacherIndex':teacherIndex})
    return response

class addNewTeacher(LoginRequiredMixin, CreateView):
    form_class = AddNewTeacherForm
    template_name = 'forms/addTeachers.html'

    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'teacherIndex'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'addNewTeacher'
        return reverse(retPage)

    def form_valid(self, form):
        return super(addNewTeacher,self).form_valid(form)


class UpdateInterest(LoginRequiredMixin,UpdateView):
    form_class = AddNewTeacherForm
    template_name = 'forms/addInterests.html'

    def get_object(self):
        return Teachers.objects.get(interestId=self.kwargs['teachid'])

    def get_success_url(self):
        return reverse('interestIndex')

def markTeacherAsInactive(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = Teachers.objects.get(pk=vol)
        ur.activeStatus = False
        ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def markTeacherAsActive(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = Teachers.objects.get(pk=vol)
        ur.activeStatus = True
        ur.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def deleteTeacher(request):
    selected_values = request.POST.getlist('UserRecs')
    for vol in selected_values:
        ur = Teachers.objects.get(pk=vol).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

