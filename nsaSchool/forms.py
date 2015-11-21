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




class NewsAdminForm(ModelForm):
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 150, 'rows': 30}))
    class Meta:
        model = VolunteerNews
        fields='__all__'




