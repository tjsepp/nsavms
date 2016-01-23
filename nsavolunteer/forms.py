from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import PrependedText
from django.forms import ModelForm
from django import forms
from .models import *
from authtools.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from tinymce.widgets import TinyMCE
from django.forms.models import inlineformset_factory
from authtools.forms import UserCreationForm
from django.forms.formsets import BaseFormSet,formset_factory


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'LoginForm'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-5'
        self.helper.layout = Layout(
            PrependedText('username','@',placeholder='email address'),
            PrependedText('password',"<span class='glyphicon glyphicon-asterisk'></span>",id="password-field", css_class="passwordfields", placeholder="password"),
            HTML('<div class="form-group"><div class="col-md-4"> </div>'),
            ButtonHolder(
                Submit('login', 'Sign in', css_class='btn-primary'),
              ),
            HTML('<div class="col-md-12" style="margin-left:12%; margin-top:3%"><a href="#">Recover Password</a>|<a href="#">Register</a></div>')
        )


class PasswordChangeFormExtra(PasswordChangeForm):
    def __init__(self, *args, **kw):
        super(PasswordChangeFormExtra, self).__init__(*args, **kw)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'LoginForm'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('old_password',"<span class='glyphicon glyphicon-asterisk'></span>",css_class="passwordfields", placeholder="Old Password"),
            PrependedText('new_password1',"<span class='glyphicon glyphicon-lock'></span>",css_class="passwordfields", placeholder="Old Password"),
            PrependedText('new_password2',"<span class='glyphicon glyphicon-lock'></span>",css_class="passwordfields", placeholder="Old Password"),
            HTML('<div class="form-group"><div class="col-md-4"> </div>'),
            ButtonHolder(
                Submit('submit', 'Reset', css_class='btn-primary'),
                HTML('<a class="btn btn-default" href="/">Cancel</a>'),
              ),
        )

class PasswordResetFormExtra(PasswordResetForm):
    def __init__(self, *args, **kw):
        super(PasswordResetFormExtra, self).__init__(*args, **kw)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            Div(
               Submit('submit', 'Reset password', css_class='btn btn-default'),
               HTML('<a class="btn btn-default" href="/">Cancel</a>'),
               css_class='text-left',
            )
        )


class AuthUserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(AuthUserUpdateForm,self).__init__(*args, **kwargs)


class UserProfileForm(ModelForm):
    class Meta:
        model = VolunteerProfile
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(UserProfileForm,self).__init__(*args, **kwargs)
        self.fields['interest'].queryset = VolunteerInterests.objects.filter(active=True).all()
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(

            Div(
            Div('firstName',css_class='col-md-6',),
            Div('lastName',css_class='col-md-6',),
            css_class='row',
            ),
            Div(
            Div('volunteerType',css_class='col-md-6',),
            Div('cellPhone',css_class='col-md-6',),
             css_class='row',
            ),

        Field('linkedUserAccount', type="hidden"),
        HTML('<h5><b>Volunteer Interests</b></h5>'),
        HTML("{% include 'forms/volunteerInterests.html' %}"),
        Field('interest', type="hidden"),
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

class FamilyProfileForm(ModelForm):
    class Meta:
        model = FamilyProfile
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(FamilyProfileForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
        'familyName',
        'streetAddress',
        'city',
        'zip',
        'homePhone',
        Field('students', type='hidden'),
        Field('specialInfo',type='hidden'),
        Field('inactiveDate',type='hidden'),
        Field('active',type='hidden'),
        Field('volunteers',type='hidden'),
         HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

class StudentUpdateForm(ModelForm):
    class Meta:
        model = Student
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(StudentUpdateForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'studentFirstName',
            'studentLastName',
            'teacher',
            'grade',
            'activeStatus',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


class AddNewFamily(ModelForm):
    class Meta:
        model=FamilyProfile
        exclude=['volunteers', 'students']

    def __init__(self, *args, **kwargs):
        super(AddNewFamily,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'familyName',
            'streetAddress',
            'city',
            'zip',
            'homePhone',
            'specialInfo',
            'inactiveDate'
            'active',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))




'''
class AddFamilyVolunteers(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.helper =FormHelper()
        self.helper.form_class='form-inline'
        self.form_method = 'post'
        self.layout = Layout(
            'name',
            'email',
            'password1',
            'password2',
        )
        self.render_required_fields = True
        self.helper.add_input(Submit('submit', 'Submit'))
        self.render_required_fields = True
        super(AddFamilyVolunteers, self).__init__(*args, **kwargs)
VolunteersFormSet = formset_factory(AddFamilyVolunteers, extra=3)

'''
class AddFamilyVolunteers(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(AddFamilyVolunteers, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].help_text=None
        self.helper = FormHelper()
        self.helper.form_class='form-inline volunteerProfile'
        self.helper.form_id='volunteerProfile'
        self.helper.layout = Layout(
            'name',
            'email',
            'password1',
            'password2',
            )
    def clean_email(self):
        try:
            User.objects.get(email = self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('This email is already in use. Please check for existing user')




class AddUserEventForm(ModelForm):
    class Meta:
        model = VolunteerHours

    def __init__(self, *args, **kwargs):
        self.famcount = len(kwargs.pop('famcount'))
        self.user= kwargs.pop('user')
        super(AddUserEventForm,self).__init__(*args, **kwargs)
        self.fields['family'].queryset = FamilyProfile.objects.filter(famvolunteers = self.user)
        self.fields['schoolYear'].initial = SchoolYear.objects.get(currentYear = 1).yearId
        if self.famcount==1:
            self.fields['family'].initial = FamilyProfile.objects.get(famvolunteers=self.user)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'

        self.helper.layout = Layout(
            'event',
            Field('eventDate', css_class='datepicker'),
            Field('volunteer',type='hidden'),
            #Field('family', type='hidden'),
            'volunteerHours',
            Field('schoolYear',type='hidden'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))
        if self.famcount>1:
            self.helper.layout.append(Field('family',css_id='LogHoursFamily'))

        else:
            self.helper.layout.append(Field('family',type='hidden'))
        self.helper.layout.append(HTML('<div class="form-group"><div class="col-lg-5"></div>'))

