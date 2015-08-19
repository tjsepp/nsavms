# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0005_auto_20150819_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalvolunteerprofile',
            name='firstName',
            field=models.CharField(max_length=200, null=True, verbose_name=b'First Name', db_column=b'firstName', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalvolunteerprofile',
            name='lastName',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Last Name', db_column=b'lastName', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='firstName',
            field=models.CharField(max_length=200, null=True, verbose_name=b'First Name', db_column=b'firstName', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='lastName',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Last Name', db_column=b'lastName', blank=True),
            preserve_default=True,
        ),
    ]
