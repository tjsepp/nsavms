# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nsavolunteer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalVolunteerProfile',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('volunteerProfileID', models.IntegerField(db_index=True, verbose_name=b'Volunteer Profile Id', db_column=b'volunteerProfileId', blank=True)),
                ('cellPhone', models.CharField(db_column=b'cellPhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'cell Phone')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('linkedUserAccount', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('volunteerType', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'volunteerType', db_constraint=False, blank=True, to='nsavolunteer.VolunteerType', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer profile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerProfile',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('volunteerProfileID', models.AutoField(serialize=False, verbose_name=b'Volunteer Profile Id', primary_key=True, db_column=b'volunteerProfileId')),
                ('cellPhone', models.CharField(db_column=b'cellPhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'cell Phone')),
                ('linkedUserAccount', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('volunteerType', models.ForeignKey(db_column=b'volunteerType', blank=True, to='nsavolunteer.VolunteerType', null=True, verbose_name=b'Volunteer Type')),
            ],
            options={
                'ordering': ['linkedUserAccount__name.split[1]'],
                'db_table': 'volunteers',
                'verbose_name_plural': 'Volunteers',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='familytouser',
            options={'verbose_name': 'User to Family', 'verbose_name_plural': 'Family to User'},
        ),
    ]
