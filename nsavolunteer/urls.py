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
url(r'^$',homeView,name='home'),
url(r'^login/$',LoginView.as_view(),name='mainlogin'),
url(r'^logout/$',LogoutView.as_view(),name='mainlogout'),
url(r'^password_recovery/$', PasswordRecoveryView.as_view(),name='password_recovery'),
url(r'^changePassword/$',ChangePassword.as_view(),name='changepassword'),
#user profile & user data
url(r'^user_profile',userSettings,name='user_profile'),
url(r'^updateProfile',UpdateVolunteerProfile.as_view(),name='updateProfile'),
url(r'^userVolunteerdata',userVolunteerData,name='userVolunteerData'),
##Admin templates
url(r'^volunteerindex',VolunteerIndex,name='volunteerIndex'),
url(r'^updateFamilyProfile/(?P<famId>\d+)$',UpdateFamilyProfile.as_view(),name='updateFamilyProfile'),
url(r'^familyindex',FamilyIndex,name='familyIndex'),
url(r'^familyprofile/(?P<famid>\d+)/$',FamilyProfilePage,name='familyprofile'),
url(r'^totalFamilyHoursCurrent',Report_Family_Hours_Current.as_view(),name='rptFamilyHoursCurrent'),
url(r'^trafficreport',TrafficReport.as_view(),name='trafficReport'),
##User and admin Forms
 url(r'^deleteloggedhours/(?P<vhoursID>\d+)',deleteLoggedHours,name='deleteUserHours'),
url(r'^updatestudent/(?P<stuId>\d+)$',UpdateStudent.as_view(),name='updatestudent'),
url(r'^loghours',logUserHours.as_view(),name='logUserHours'),
url(r'^edithours/(?P<vhoursID>\d+)$',updateUserHours.as_view(),name='editUserHours'),
url(r'^addinterest/(?P<Intid>\d+)/$',addInterestToProfile,name='addinterestToProfile'),
url(r'^addfamily$',CreateFamily.as_view(),name='addfamily'),
url(r'^adduserstofamily/(?P<famid>\d+)/$',AddVolunteersToNewFamily,name='addusertofamily'),
url(r'^processContacttofamily/(?P<famid>\d+)/$',ProcessContactToExistingFamily,name='processContactToFamily'),
url(r'^addContacttofamily/(?P<famid>\d+)/$',addContactToExistingFamily,name='addContactToExistingFamily'),
url(r'^removeContactFromFamily/(?P<famid>\d+)/(?P<volunteerid>\d+)/$',RemoveContactFromFamily,name='removeContactFromFamily'),
url(r'^addTrafficVolunteers/$',AddTrafficVolunteers,name='addtrafficvolunteers'),
url(r'^deleteinterest/(?P<Intid>\d+)/$',deleteInterestFromProfile,name='deleteinterestFromProfile'),
url(r'^markpending$',markAsPending,name='markAsPending'),
url(r'^markApproved$',markAsApproved,name='markAsApproved'),
url(r'^deactivateuser$',deactivateVolunteerAccount,name='deactivateUserAccount'),
url(r'^activateuser$',activateVolunteerAccount,name='activateUserAccount'),
url(r'^addVolunteer_woFamily$',addVolunteer_woFamily,name='addVolunteer_woFamily'),
url(r'^get_tasks/', 'nsavolunteer.views.get_tasks', name='get_tasks'),
]

