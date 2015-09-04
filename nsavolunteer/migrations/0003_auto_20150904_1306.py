# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0002_auto_20150904_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familytouser',
            name='organization',
            field=models.ForeignKey(verbose_name=b'Related Family', to='nsavolunteer.FamilyProfile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='familytouser',
            name='user',
            field=models.ForeignKey(verbose_name=b'Family', to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=True,
        ),
    ]
