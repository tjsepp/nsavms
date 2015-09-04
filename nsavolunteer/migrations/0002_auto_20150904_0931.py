# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalvolunteerinterests',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Active', db_column=b'active'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volunteerinterests',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Active', db_column=b'active'),
            preserve_default=True,
        ),
    ]
