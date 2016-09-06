from django.contrib import admin
from models import VolunteerInterests,VolunteerType,FamilyProfile,VolunteerProfile, RewardCardUsers,Student,\
    FamilyProfile,StudentToFamily,RewardCardUsage,VolunteerHours,FamilyAggHours, Traffic_Duty
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from django.forms import TextInput, Textarea
from django.db import models



def mark_approved(modeladmin, request, queryset):
    queryset.update(volStatus='approved')
mark_approved.short_description = "Mark selected users as approved"

def mark_pending(modeladmin, request, queryset):
    queryset.update(volStatus='pending')
mark_pending.short_description = "Mark selected users as pending"

class VolunteerProfileAdmin(SimpleHistoryAdmin):
    model = VolunteerProfile
    search_fields = ('firstName','lastName')
    filter_horizontal = ('interest',)
    list_display = ('linkedUserAccount','firstName','lastName','volunteerType','cellPhone')
    raw_id_fields = ('linkedUserAccount',)
    actions = [mark_approved,mark_pending]



class RewardCardInfoAdmin(admin.ModelAdmin):
    model = RewardCardUsers
    list_display = ('linkedUser','storeName','customerCardNumber')
    list_filter = ('storeName',)


class RewardCardDataAdmin(admin.ModelAdmin):
    models= RewardCardUsage
    list_display = ('storeName','schoolYear')
    list_editable = ('schoolYear',)


def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Mark selected records as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Mark selected records as inactive"

class FamilyProfileAdmin(SimpleHistoryAdmin):
    model = FamilyProfile
    search_fields = ('familyName',)
    filter_horizontal = ('famvolunteers',)
    list_display = ('familyName','active','streetAddress','city','homePhone',)
    actions = [make_active,make_inactive]



class StudentAdmin(SimpleHistoryAdmin):
    model = Student
    list_display = ('getFullStudentName','activeStatus','grade','teacher')
    list_editable = ('grade','teacher',)


class VolunteerHoursAdmin(SimpleHistoryAdmin):
    model = VolunteerHours
    search_fields = ('volunteer__name','event__eventName','family__familyName')
    list_display = ('volunteer','family','event','eventDate','dateCreated','volunteerHours','approved')
    list_filter = ('eventDate','dateCreated',)


class FamilyAggHoursAdmin(SimpleHistoryAdmin):
    model = VolunteerHours
    list_display = ('family','schoolYear','totalVolHours','trafficDutyCount')



#admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
#admin.site.register(Volunteers,VolunteerAdmin)
admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
admin.site.register(VolunteerInterests,SimpleHistoryAdmin)
admin.site.register(VolunteerType,SimpleHistoryAdmin)
admin.site.register(FamilyProfile,FamilyProfileAdmin)
#admin.site.register(VolunteerToFamily,UserToFamilyAdmin)
#admin.site.register(FamilyProfileOwner)
admin.site.register(Student,StudentAdmin)
admin.site.register(StudentToFamily)
admin.site.register(RewardCardUsage,RewardCardDataAdmin)
admin.site.register(RewardCardUsers,RewardCardInfoAdmin)
admin.site.register(VolunteerHours,VolunteerHoursAdmin)
admin.site.register(FamilyAggHours,FamilyAggHoursAdmin)
admin.site.register(Traffic_Duty)
#admin.site.register(RecruitingEmail)