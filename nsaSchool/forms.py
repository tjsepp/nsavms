from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button, HTML
from crispy_forms.bootstrap import PrependedText
from django.forms import ModelForm
from django import forms
from .models import *
from authtools.models import User
from tinymce.widgets import TinyMCE
from nsavolunteer.models import Student



class NewsAdminForm(ModelForm):
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 150, 'rows': 30}))
    class Meta:
        model = VolunteerNews
        fields='__all__'

class AddNewTeacherForm(ModelForm):
    class Meta:
        model=Teachers

    def __init__(self, *args, **kwargs):
        super(AddNewTeacherForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'firstName',
            'lastName',
            'gradeLevel',
            'activeStatus',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


