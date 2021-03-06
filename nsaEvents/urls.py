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

##Base files

url(r'^addVolunteerEvent',addVolunteerEvent.as_view(),name='addVolunteerEvent'),
url(r'^editVolunteerEvent/(?P<eventID>\d+)$',updateVolunteerEvent.as_view(),name='editVolunteerEvent'),
url(r'^eventIndex',EventIndex,name='eventIndex'),
url(r'^TaskIndex',EventTaskIndex,name='taskIndex'),
url(r'^addEventTask',addVolunteerEventTask.as_view(),name='addEventTask'),
url(r'^editEventTask/(?P<taskID>\d+)$',updateVolunteerEventTask.as_view(),name='editEventTask'),
url(r'^log_hours_from_event/(?P<eventId>\d+)$',LogHoursFromEvent.as_view(),name='log_hours_from_event'),
url(r'^edit_hours_from_event/(?P<vhoursID>\d+)$',UpdateLoggedHoursFromEvent.as_view(),name='edit_hours_from_event'),
url(r'^delete_hours_from_event/(?P<vhoursID>\d+)$',deleteLoggedHoursfromevent,name='delete_hours_from_event'),
url(r'^get_related_families/(?P<usid>\d+)',get_related_families,name='GetFam')
]

