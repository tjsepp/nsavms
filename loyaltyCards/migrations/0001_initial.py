# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nsavolunteer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltyCardNumbers',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('loyaltyCardID', models.AutoField(serialize=False, verbose_name=b'Loyalty Card Id', primary_key=True, db_column=b'loyaltyCardId')),
                ('loyaltyCardNumber', models.CharField(max_length=20, verbose_name=b'Loyalty Card Number', db_column=b'loyaltyCardNumber')),
                ('alternateId', models.CharField(max_length=10, null=True, verbose_name=b'Alternate ID', db_column=b'alternateId', blank=True)),
                ('relatedFamily', models.ForeignKey(db_column=b'relatedFamily', verbose_name=b'Family', to='nsavolunteer.FamilyProfile')),
            ],
            options={
                'ordering': ['dateCreated'],
                'db_table': 'loyaltyCardNumbers',
                'verbose_name_plural': 'Loyalty Card Numbers',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='loyaltycardnumbers',
            unique_together=set([('loyaltyCardNumber', 'relatedFamily')]),
        ),
    ]
