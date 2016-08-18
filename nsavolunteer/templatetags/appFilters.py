from django import template
from ..models import VolunteerProfile
from authtools.models import User
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_avc')
def is_avc(value):
    x_true = 0
    permList = value
    for x in permList:
        if x.name =='AVC':
            x_true=1
    if x_true ==1:
        return "<span class='glyphicon glyphicon-ok' style='color: green;'><div style='display: none;'>True</div></span>"


