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
from nsavolunteer.models import VolunteerHours, FamilyProfile, VolunteerProfile
from nsaSchool.models import SchoolYear

class EventsForm(ModelForm):
    class Meta:
        model = NsaEvents
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(EventsForm,self).__init__(*args, **kwargs)
        self.fields['eventLeader'].queryset = User.objects.filter(Q(groups__name='AVC')|Q(groups__name='VolunteerManager'))
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
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

class EventTasksForm(ModelForm):
    class Meta:
        model = EventTasks
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(EventTasksForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
        'relatedEvent',
        'taskName',
        'allowView',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))



class LogHoursFromEventForm(ModelForm):
    '''
    This class allows admins to log volunteer hours from events
    '''
    class Meta:
        model = VolunteerHours
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        self.famcount = len(kwargs.pop('famcount'))
        self.user= kwargs.pop('user')
        super(LogHoursFromEventForm,self).__init__(*args, **kwargs)
        self.fields['event'].queryset = NsaEvents.objects.filter(allowView=True)
        self.fields['schoolYear'].initial = SchoolYear.objects.get(currentYear = 1).yearId
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'

        self.helper.layout = Layout(
            Field('volunteer', css_class ='volunteerSelect'),
            Field('eventDate', css_class='datepicker',placeholder='Select Date'),
            Field('event', type='hidden'),
            Field('task', css_id='task', css_class='typeahead'),
            Field('family', css_id='familySelect'),
            Field('volunteerHours',placeholder='Enter Number Of Hours'),
                  HTML(
                """
                <div class="row timeEntry">
                    <div class="col-lg-6">
                        <div class="input-group bootstrap-timepicker timepicker">
                        <input id="timepicker1" type="text" class="form-control input-small" placeholder="Start Time">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-time"></i></span>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="input-group bootstrap-timepicker timepicker-orient-bottom">
                        <input id="timepicker2" type="text" class="form-control input-small" placeholder="End Time">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-time" id='pickIcon2'></i></span>
                    </div>
                </div>
                <div class='col-md-12' style='color:red; display: none; margin-bottom:2%' id='dataWarning'></div>
                </div>
            """
            ),
            Field('schoolYear',type='hidden'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

        self.helper.layout.append(HTML('<div class="form-group"><div class="col-lg-5"></div>'))

