# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '0003_auto_20150904_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familytouser',
            name='user',
            field=models.ForeignKey(verbose_name=b'User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
