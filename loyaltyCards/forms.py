from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import PrependedText
from django.forms import ModelForm
from django import forms
from loyaltyCards.models import *
from nsavolunteer.models import FamilyProfile
from authtools.models import User
from django.forms.formsets import BaseFormSet,formset_factory
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q
from nsavolunteer.models import VolunteerHours, FamilyProfile, VolunteerProfile
from nsaSchool.models import SchoolYear



class AddLoyaltyCardNumberForm(ModelForm):
    class Meta:
        model = LoyaltyCardNumbers
        fields='__all__'
    def __init__(self, *args, **kwargs):
        self.famcount = len(kwargs.pop('famcount'))
        self.user = kwargs.pop('user')
        super(AddLoyaltyCardNumberForm,self).__init__(*args, **kwargs)
        if self.famcount==1:
            self.fields['relatedFamily'].initial = FamilyProfile.objects.get(famvolunteers=self.user)
        self.fields['relatedFamily'].queryset = FamilyProfile.objects.filter(famvolunteers=self.user)
        self.fields['loyaltyCardNumber'].help_text = "***Enter loyalty card number without spaces"
        self.fields['alternateId'].help_text = "***Alternate ID is the phone number tied to the account. Please enter 10 digit phone number without any spaces or dashes"
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
        'loyaltyCardNumber',
        'alternateId',
        HTML('<div class="form-group"><div class="col-md-12"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another Card', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))
        if self.famcount>1:
            self.helper.layout.append(Field('relatedFamily',css_id='LogHoursFamily'))

        else:
            self.helper.layout.append(Field('relatedFamily',type='hidden'))
        self.helper.layout.append(HTML('<div class="form-group"><div class="col-lg-5"></div>'))
