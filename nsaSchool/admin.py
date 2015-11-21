from django.contrib import admin
from models import SchoolYear,GradeLevel,Teachers,VolunteerNews
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from django.forms import TextInput, Textarea
from django.db import models
from forms import  NewsAdminForm

class SchoolYearAdmin(admin.ModelAdmin):
    model = SchoolYear
    list_display = ('schoolYear','currentYear')

class VolunteerNewsAdmin(SimpleHistoryAdmin):
    form = NewsAdminForm

admin.site.register(SchoolYear,SchoolYearAdmin)
admin.site.register(GradeLevel)
admin.site.register(Teachers)
admin.site.register(VolunteerNews,VolunteerNewsAdmin)