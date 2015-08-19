# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0002_auto_20150818_1445'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='volunteerprofile',
            options={'ordering': ['linkedUserAccount__name'], 'verbose_name_plural': 'VolunteerProfile'},
        ),
        migrations.AlterModelTable(
            name='volunteerprofile',
            table='volunteerProfile',
        ),
    ]
