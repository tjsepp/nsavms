"""nsavol URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import *

urlpatterns = [

url(r'^teacherIndex$',TeacherIndex,name='teacherIndex'),
url(r'^addNewTeacher$',addNewTeacher.as_view(),name='addNewTeacher'),
url(r'^makeTeacherInActive$',markTeacherAsInactive,name='inactiveTeacher'),
url(r'^makeTeacherActive$',markTeacherAsActive,name='activeTeacher'),
url(r'^deleteTeacher$',deleteTeacher,name='deleteTeachers'),
url(r'^editTeacher/(?P<teachid>\d+)$',UpdateTeacher.as_view(),name='editTeacher'),
url(r'^teacher_profile/(?P<teachid>\d+)$',teacherProfile,name='teacherProfile'),
url(r'^class_assignment/(?P<teachid>\d+)$',StudentToTeacherAssignment,name='teacherAssignment'),
url(r'^assign_students/(?P<teachid>\d+)$',assignStudents,name='assignStudents'),
]

#addNewTeacher

