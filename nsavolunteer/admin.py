from django.contrib import admin
from models import VolunteerInterests,VolunteerType,FamilyProfile,VolunteerToFamily,VolunteerProfile, RewardCardUsers,Student,FamilyProfile,VolunteerToFamily,StudentToFamily
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from django.forms import TextInput, Textarea
from django.db import models



class VolunteerProfileAdmin(SimpleHistoryAdmin):
    model = VolunteerProfile
    search_fields = ('firstName','lastName')
    filter_horizontal = ('interest',)
    list_display = ('linkedUserAccount','firstName','lastName','volunteerType','cellPhone')
    raw_id_fields = ('linkedUserAccount',)


class UserToFamilyForm(forms.ModelForm):
    '''This form is used in the UserToFamilyAdmin to help clean up the labels ex. change from organization to Family
    '''
    organization = forms.ModelChoiceField(queryset=FamilyProfile.objects.all(),label='Family')
    class Meta:
        model = VolunteerToFamily
        fields = '__all__'

class UserToFamilyAdmin(SimpleHistoryAdmin):
    '''
    Uses custom form to clean up labels
    '''
    model = VolunteerToFamily
    form = UserToFamilyForm

class RewardCardInfoAdmin(admin.ModelAdmin):
    model = RewardCardUsers
    list_display = ('linkedUser','storeName','customerCardNumber')
    list_filter = ('storeName',)

class userToProfileInline(admin.TabularInline):
    '''
    Inline that provides the family profile with the list of related users.
    '''
    model = VolunteerToFamily
    extra = 0
    verbose_name = "Family Volunteer"
    verbose_name_plural = "Family Volunteers"

class FamilyProfileAdmin(SimpleHistoryAdmin):
    inlines = [userToProfileInline]






#admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
#admin.site.register(Volunteers,VolunteerAdmin)
admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
admin.site.register(VolunteerInterests,SimpleHistoryAdmin)
admin.site.register(VolunteerType,SimpleHistoryAdmin)
admin.site.register(FamilyProfile,FamilyProfileAdmin)
admin.site.register(VolunteerToFamily,UserToFamilyAdmin)
#admin.site.register(FamilyProfileOwner)
admin.site.register(Student)
admin.site.register(StudentToFamily)
admin.site.register(RewardCardUsers,RewardCardInfoAdmin)