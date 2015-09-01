# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import organizations.base


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name of the organization', max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('streetAddress', models.CharField(max_length=200, null=True, verbose_name=b'Street Address', db_column=b'streetAddress', blank=True)),
                ('city', models.CharField(max_length=50, null=True, verbose_name=b'city', db_column=b'city', blank=True)),
                ('zip', models.CharField(max_length=15, null=True, verbose_name=b'zip', db_column=b'zip', blank=True)),
                ('homePhone', models.CharField(db_column=b'homePhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'Home Phone')),
                ('specialInfo', models.TextField(null=True, verbose_name=b'Volunteer Note', db_column=b'VolunteerNote', blank=True)),
                ('inactiveDate', models.DateField(null=True, verbose_name=b'Inactive Date', db_column=b'inactiveDate', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name=b'active', db_column=b'active')),
            ],
            options={
                'db_table': 'familyProfile',
                'verbose_name_plural': 'Family Profile',
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FamilyProfileOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization', models.OneToOneField(related_name='owner', to='nsavolunteer.FamilyProfile')),
            ],
            options={
                'db_table': 'familyProfileowner',
                'verbose_name_plural': 'Family Profile Owner',
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FamilyToUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization', models.ForeignKey(related_name='organization_users', to='nsavolunteer.FamilyProfile')),
                ('user', models.ForeignKey(related_name='nsavolunteer_familytouser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'familytouser',
                'verbose_name': 'User to Family',
                'verbose_name_plural': 'Family to User',
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalFamilyProfile',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('name', models.CharField(help_text='The name of the organization', max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('streetAddress', models.CharField(max_length=200, null=True, verbose_name=b'Street Address', db_column=b'streetAddress', blank=True)),
                ('city', models.CharField(max_length=50, null=True, verbose_name=b'city', db_column=b'city', blank=True)),
                ('zip', models.CharField(max_length=15, null=True, verbose_name=b'zip', db_column=b'zip', blank=True)),
                ('homePhone', models.CharField(db_column=b'homePhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'Home Phone')),
                ('specialInfo', models.TextField(null=True, verbose_name=b'Volunteer Note', db_column=b'VolunteerNote', blank=True)),
                ('inactiveDate', models.DateField(null=True, verbose_name=b'Inactive Date', db_column=b'inactiveDate', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name=b'active', db_column=b'active')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical family profile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalVolunteerInterests',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('interestId', models.IntegerField(db_index=True, verbose_name=b'Interest Id', db_column=b'interestId', blank=True)),
                ('interestName', models.CharField(max_length=200, null=True, verbose_name=b'Interest', db_column=b'interestName')),
                ('description', models.TextField(null=True, verbose_name=b'Interest Description', db_column=b'interestDescription', blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer interests',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalVolunteerNews',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('newsID', models.IntegerField(db_index=True, verbose_name=b'VolunteerNewsId', db_column=b'newsID', blank=True)),
                ('headline', models.CharField(default=None, max_length=250, null=True, verbose_name=b'News Title', db_column=b'title')),
                ('body', models.TextField(null=True, verbose_name=b'News Body', db_column=b'body')),
                ('newsEndDate', models.DateField(help_text=b'For indefinite news, enter 1/1/2900', null=True, verbose_name=b'NewsEndDate', db_column=b'enddate')),
                ('topPriority', models.BooleanField(default=False, verbose_name=b'Top priority', db_column=b'prioriyy')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer news',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalVolunteerProfile',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('volunteerProfileID', models.IntegerField(db_index=True, verbose_name=b'Volunteer Profile Id', db_column=b'volunteerProfileId', blank=True)),
                ('firstName', models.CharField(max_length=200, null=True, verbose_name=b'First Name', db_column=b'firstName', blank=True)),
                ('lastName', models.CharField(max_length=200, null=True, verbose_name=b'Last Name', db_column=b'lastName', blank=True)),
                ('cellPhone', models.CharField(db_column=b'cellPhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'cell Phone')),
                ('doNotEmail', models.BooleanField(default=False, verbose_name=b'Do Not Email', db_column=b'emailOptOut')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('linkedUserAccount', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer profile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalVolunteerType',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('volunteerTypeId', models.IntegerField(db_index=True, verbose_name=b'Volunteer Type ID', db_column=b'volunteerTypeId', blank=True)),
                ('volunteerType', models.CharField(max_length=200, null=True, verbose_name=b'Volunteer Type', db_column=b'volunteerType')),
                ('description', models.TextField(null=True, verbose_name=b'Volunteer Type Description', db_column=b'volTypeDescription', blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerInterests',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('interestId', models.AutoField(serialize=False, verbose_name=b'Interest Id', primary_key=True, db_column=b'interestId')),
                ('interestName', models.CharField(max_length=200, null=True, verbose_name=b'Interest', db_column=b'interestName')),
                ('description', models.TextField(null=True, verbose_name=b'Interest Description', db_column=b'interestDescription', blank=True)),
            ],
            options={
                'ordering': ['interestName'],
                'db_table': 'volunteerInterests',
                'verbose_name_plural': 'Interest Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerNews',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('newsID', models.AutoField(serialize=False, verbose_name=b'VolunteerNewsId', primary_key=True, db_column=b'newsID')),
                ('headline', models.CharField(default=None, max_length=250, null=True, verbose_name=b'News Title', db_column=b'title')),
                ('body', models.TextField(null=True, verbose_name=b'News Body', db_column=b'body')),
                ('newsEndDate', models.DateField(help_text=b'For indefinite news, enter 1/1/2900', null=True, verbose_name=b'NewsEndDate', db_column=b'enddate')),
                ('topPriority', models.BooleanField(default=False, verbose_name=b'Top priority', db_column=b'prioriyy')),
            ],
            options={
                'ordering': ['dateCreated'],
                'db_table': 'volunteerNews',
                'verbose_name_plural': 'Volunteer News',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerProfile',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('volunteerProfileID', models.AutoField(serialize=False, verbose_name=b'Volunteer Profile Id', primary_key=True, db_column=b'volunteerProfileId')),
                ('firstName', models.CharField(max_length=200, null=True, verbose_name=b'First Name', db_column=b'firstName', blank=True)),
                ('lastName', models.CharField(max_length=200, null=True, verbose_name=b'Last Name', db_column=b'lastName', blank=True)),
                ('cellPhone', models.CharField(db_column=b'cellPhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'cell Phone')),
                ('doNotEmail', models.BooleanField(default=False, verbose_name=b'Do Not Email', db_column=b'emailOptOut')),
                ('interest', models.ManyToManyField(related_name='profile_interest', to='nsavolunteer.VolunteerInterests', db_table=b'profileToInterest', blank=True, null=True, verbose_name=b'Volunteer Interests')),
                ('linkedUserAccount', models.OneToOneField(related_name='linkedUser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['linkedUserAccount__name'],
                'db_table': 'volunteerProfile',
                'verbose_name_plural': 'Volunteer Profile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerType',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('volunteerTypeId', models.AutoField(serialize=False, verbose_name=b'Volunteer Type ID', primary_key=True, db_column=b'volunteerTypeId')),
                ('volunteerType', models.CharField(max_length=200, null=True, verbose_name=b'Volunteer Type', db_column=b'volunteerType')),
                ('description', models.TextField(null=True, verbose_name=b'Volunteer Type Description', db_column=b'volTypeDescription', blank=True)),
            ],
            options={
                'ordering': ['volunteerType'],
                'db_table': 'volunteerType',
                'verbose_name_plural': 'Volunteer Type',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='volunteerType',
            field=models.ForeignKey(db_column=b'volunteerType', blank=True, to='nsavolunteer.VolunteerType', null=True, verbose_name=b'Volunteer Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalvolunteerprofile',
            name='volunteerType',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'volunteerType', db_constraint=False, blank=True, to='nsavolunteer.VolunteerType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyprofileowner',
            name='organization_user',
            field=models.OneToOneField(to='nsavolunteer.FamilyToUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyprofile',
            name='users',
            field=models.ManyToManyField(related_name='nsavolunteer_familyprofile', through='nsavolunteer.FamilyToUser', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
