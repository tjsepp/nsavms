"""Loyalty CardURL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import *

urlpatterns = [

##Base files

url(r'^addLoyaltyCard',addLoyaltyCardNumber.as_view(),name='addNewLoyaltyCard'),

]
