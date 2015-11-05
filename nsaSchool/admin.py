from django.contrib import admin
from models import SchoolYear,GradeLevel,Teachers
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from django.forms import TextInput, Textarea
from django.db import models


class SchoolYearAdmin(admin.ModelAdmin):
    model = SchoolYear
    list_display = ('schoolYear','currentYear')

admin.site.register(SchoolYear,SchoolYearAdmin)
admin.site.register(GradeLevel)
admin.site.register(Teachers)