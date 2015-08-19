# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0003_auto_20150818_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerprofile',
            name='interest',
            field=models.ManyToManyField(related_name='profile_interest', to='nsavolunteer.VolunteerInterests', db_table=b'profileToInterest', blank=True, null=True, verbose_name=b'Volunteer Interests'),
            preserve_default=True,
        ),
    ]
