from django.shortcuts import render
from models import Teachers
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, \
        ListView, DeleteView,TemplateView
from braces.views import LoginRequiredMixin
from forms import AddNewTeacherForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from nsavolunteer.models import Student


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


#@login_required
def teacherProfile(request, teachid):
    teacher = Teachers.objects.get(pk= teachid)
    students = Student.objects.filter(teacher = teacher.teacherId).all().order_by('studentLastName')
    request.session['teachUpdate']= teacher.teacherId
    #rewardCards = RewardCardUsers.objects.filter(linkedUser=request.user).all()
    response = render(request, 'profiles/teacherProfile.html',{'teacher':teacher,'students':students})
    return response


class UpdateTeacher(LoginRequiredMixin,UpdateView):
    form_class = AddNewTeacherForm
    template_name = 'forms/addTeachers.html'

    def get_object(self):
        return Teachers.objects.get(teacherId=self.kwargs['teachid'])

    def get_success_url(self):
        if self.request.POST.get('save'):
            retPage = 'teacherIndex'
        elif self.request.POST.get('saveAndAdd'):
            retPage = 'addNewTeacher'
        return reverse(retPage)

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateTeacher, self).get_context_data(*args, **kwargs)
        previous_page = self.request.META['HTTP_REFERER']
        print previous_page
        context['isEdit'] = 'Edit'
        return context

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


def StudentToTeacherAssignment(request,teachid):
    teach=Teachers.objects.get(pk=teachid)
    students = Student.objects.filter(grade = teach.gradeLevel).filter(teacher=None)
    response = render(request, 'tables/classAssignment.html',{'teacher':teach,'students':students})
    return response

def assignStudents(request,teachid):
    selected_values = request.POST.getlist('UserRecs')
    for stu in selected_values:
        print stu
        student = Student.objects.get(pk=stu)
        student.teacher=Teachers.objects.get(pk=teachid)
        student.save()
    return HttpResponseRedirect(reverse('teacherProfile', kwargs={'teachid': teachid}))