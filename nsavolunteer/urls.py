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
url(r'^$',homeView,name='home'),
url(r'^user_dashboard',userSettings,name='user_dashboard'),
url(r'^updateProfile',UpdateVolunteerProfile.as_view(),name='updateProfile'),
url(r'^userVolunteerdata',userVolunteerData,name='userVolunteerData'),
url(r'^volunteerInterests',InterestList,name='volunteerInterests'),
url(r'^addinterest/(?P<Intid>\d+)/$',addInterestToProfile,name='addinterestToProfile'),
url(r'^deleteinterest/(?P<Intid>\d+)/$',deleteInterestFromProfile,name='deleteinterestFromProfile'),
url(r'^login/$',LoginView.as_view(),name='mainlogin'),
url(r'^logout/$',LogoutView.as_view(),name='mainlogout'),


]

