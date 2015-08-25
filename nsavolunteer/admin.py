from django.contrib import admin
from models import VolunteerInterests,VolunteerType,FamilyProfile,FamilyProfileOwner,FamilyToUser,VolunteerProfile
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from authtools.models import User
# Register your models here.
from organizations.models import (Organization, OrganizationUser,
    OrganizationOwner)
#from organizations.forms import UserAdminForm
#from organizations.models import Account, AccountUser



class VolunteerProfileAdmin(SimpleHistoryAdmin):
    model = VolunteerProfile
    list_display = ('firstName','lastName','volunteerType','cellPhone')


class UserToFamilyForm(forms.ModelForm):
    '''This form is used in the UserToFamilyAdmin to help clean up the labels ex. change from organization to Family
    '''
    organization = forms.ModelChoiceField(queryset=FamilyProfile.objects.all(),label='Family')
    class Meta:
        model = FamilyToUser
        fields = '__all__'

class UserToFamilyAdmin(SimpleHistoryAdmin):
    '''
    Uses custom form to clean up labels
    '''
    model = FamilyToUser
    form = UserToFamilyForm


class userToProfileInline(admin.TabularInline):
    '''
    Inline that provides the family profile with the list of related users.
    '''
    model = FamilyToUser
    extra = 0

class FamilyProfileAdmin(SimpleHistoryAdmin):
    inlines = [userToProfileInline]



#admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
#admin.site.register(Volunteers,VolunteerAdmin)
admin.site.register(VolunteerProfile,VolunteerProfileAdmin)
admin.site.register(VolunteerInterests,SimpleHistoryAdmin)
admin.site.register(VolunteerType,SimpleHistoryAdmin)
admin.site.register(FamilyProfile,FamilyProfileAdmin)
admin.site.register(FamilyToUser,UserToFamilyAdmin)
admin.site.register(FamilyProfileOwner)