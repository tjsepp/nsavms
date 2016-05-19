from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import PrependedText
from django.forms import ModelForm
from django import forms
from .models import *
from authtools.models import User
from django.forms.models import inlineformset_factory
from authtools.forms import UserCreationForm
from django.forms.formsets import BaseFormSet,formset_factory
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q

class EventsForm(ModelForm):
    class Meta:
        model = NsaEvents
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(EventsForm,self).__init__(*args, **kwargs)
        self.fields['eventLeader'].queryset = User.objects.filter(Q(groups__name='ACV')|Q(groups__name='VolunteerManager'))
        self.fields['daysOfWeek'].widget = forms.CheckboxSelectMultiple()
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
        'eventName',
        Field('eventDate', css_class='datepicker',placeholder='Select Date'),
        'eventLeader',
        'location',
        'autoApprove',
        'description',
        'internalComments',
        'recurring',
        'daysOfWeek',
        'allowView',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))