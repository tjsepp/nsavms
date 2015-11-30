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
        self.helper.form_class='form-hprizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
            'firstName',
            'lastName',
            'volunteerType',
            'cellPhone',
            'interest',
        Field('linkedUserAccount', type="hidden"),
        self.helper.add_input(Submit('save', 'Save')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        )

class FamilyProfileForm(ModelForm):
    class Meta:
        model = FamilyProfile
        fields='__all__'

class AddNewFamily(ModelForm):
    class Meta:
        model=FamilyProfile
        fields='__all__'


