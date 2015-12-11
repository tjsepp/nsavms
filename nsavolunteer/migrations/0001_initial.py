# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nsaSchool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyProfile',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('familyProfileId', models.AutoField(serialize=False, verbose_name=b'Family Profile Id', primary_key=True, db_column=b'FamilyProfileId')),
                ('familyName', models.CharField(default=None, max_length=50, null=True, verbose_name=b'Family Name', db_column=b'familyName')),
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
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalFamilyProfile',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('familyProfileId', models.IntegerField(db_index=True, verbose_name=b'Family Profile Id', db_column=b'FamilyProfileId', blank=True)),
                ('familyName', models.CharField(default=None, max_length=50, null=True, verbose_name=b'Family Name', db_column=b'familyName')),
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
            name='HistoricalRewardCardUsers',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('RewardCardId', models.IntegerField(db_index=True, verbose_name=b'Reward Card ID', db_column=b'rewardCardId', blank=True)),
                ('storeName', models.CharField(max_length=25, null=True, verbose_name=b'Store', db_column=b'store', choices=[(b'King Soopers', b'King Soopers'), (b'Safeway', b'Safeway')])),
                ('customerCardNumber', models.CharField(max_length=50, null=True, verbose_name=b'Card Number', db_column=b'cardNumber')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('linkedUser', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'linkedUser', db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical reward card users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalStudent',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('studentId', models.IntegerField(db_index=True, verbose_name=b'StudentId', db_column=b'studentId', blank=True)),
                ('studentName', models.CharField(max_length=100, null=True, verbose_name=b'Student Name', db_column=b'studentName')),
                ('activeStatus', models.BooleanField(default=True, verbose_name=b'Active Status', db_column=b'activeStatus')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('grade', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'gradeLevel', db_constraint=False, blank=True, to='nsaSchool.GradeLevel', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('teacher', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'teacher', db_constraint=False, blank=True, to='nsaSchool.Teachers', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical student',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalStudentToFamily',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('group', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='nsavolunteer.FamilyProfile', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical student to family',
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
                ('active', models.BooleanField(default=True, verbose_name=b'Active', db_column=b'active')),
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
            name='HistoricalVolunteerProfile',
            fields=[
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('volunteerProfileID', models.IntegerField(db_index=True, verbose_name=b'Volunteer Profile Id', db_column=b'volunteerProfileId', blank=True)),
                ('firstName', models.CharField(max_length=200, null=True, verbose_name=b'First Name', db_column=b'firstName', blank=True)),
                ('lastName', models.CharField(max_length=200, null=True, verbose_name=b'Last Name', db_column=b'lastName', blank=True)),
                ('cellPhone', models.CharField(db_column=b'cellPhone', default=None, max_length=15, blank=True, null=True, verbose_name=b'cell Phone')),
                ('volStatus', models.CharField(db_column=b'volStatus', default=b'pending', choices=[(b'pending', b'Pending'), (b'approved', b'Approved')], max_length=15, blank=True, null=True, verbose_name=b'Volunteer Status')),
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
            name='HistoricalVolunteerToFamily',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('dateCreated', models.DateTimeField(editable=False, blank=True)),
                ('dateUpdated', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('group', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='nsavolunteer.FamilyProfile', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('person', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical volunteer to family',
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
            name='RewardCardUsage',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('rewardCardusageId', models.AutoField(serialize=False, verbose_name=b'Reward Card Usage ID', primary_key=True, db_column=b'rewardCardUsageId')),
                ('customerCardNumber', models.CharField(max_length=50, null=True, verbose_name=b'Card Number', db_column=b'customerCardNumber')),
                ('refillDate', models.DateField(null=True, verbose_name=b'Refill Date', db_column=b'refillDate', blank=True)),
                ('refillValue', models.DecimalField(decimal_places=2, verbose_name=b'Refill Value', max_digits=8, db_column=b'refillValue')),
                ('volunteerHours', models.DecimalField(db_column=b'volunteerHours', decimal_places=3, max_digits=8, blank=True, null=True, verbose_name=b'Volunteer Hours')),
                ('storeName', models.CharField(max_length=25, null=True, verbose_name=b'Store', db_column=b'store', choices=[(b'King Soopers', b'King Soopers'), (b'Safeway', b'Safeway')])),
                ('schoolYear', models.ForeignKey(db_column=b'SchoolYear', verbose_name=b'School Year', to='nsaSchool.SchoolYear', null=True)),
                ('volunteerId', models.ForeignKey(related_name='rewardCardValue', db_column=b'volunteer', blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name=b'Volunteer')),
            ],
            options={
                'ordering': ['refillDate'],
                'db_table': 'rewardCardData',
                'verbose_name_plural': 'Reward Card Data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RewardCardUsers',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('RewardCardId', models.AutoField(serialize=False, verbose_name=b'Reward Card ID', primary_key=True, db_column=b'rewardCardId')),
                ('storeName', models.CharField(max_length=25, null=True, verbose_name=b'Store', db_column=b'store', choices=[(b'King Soopers', b'King Soopers'), (b'Safeway', b'Safeway')])),
                ('customerCardNumber', models.CharField(max_length=50, null=True, verbose_name=b'Card Number', db_column=b'cardNumber')),
                ('linkedUser', models.ForeignKey(related_name='rewardCardUser', db_column=b'linkedUser', verbose_name=b'LinkedUser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['dateCreated'],
                'db_table': 'rewardCardUserInformation',
                'verbose_name_plural': 'Reward Card User Information',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('studentId', models.AutoField(serialize=False, verbose_name=b'StudentId', primary_key=True, db_column=b'studentId')),
                ('studentName', models.CharField(max_length=100, null=True, verbose_name=b'Student Name', db_column=b'studentName')),
                ('activeStatus', models.BooleanField(default=True, verbose_name=b'Active Status', db_column=b'activeStatus')),
                ('grade', models.ForeignKey(db_column=b'gradeLevel', blank=True, to='nsaSchool.GradeLevel', null=True, verbose_name=b'Grade Level')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, db_column=b'teacher', blank=True, to='nsaSchool.Teachers', null=True)),
            ],
            options={
                'ordering': ['studentName'],
                'db_table': 'students',
                'verbose_name_plural': 'Students',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentToFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='nsavolunteer.FamilyProfile')),
                ('student', models.ForeignKey(to='nsavolunteer.Student')),
            ],
            options={
                'ordering': ['student'],
                'db_table': 'studentToFamily',
                'verbose_name_plural': 'Student To Family',
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
                ('active', models.BooleanField(default=True, verbose_name=b'Active', db_column=b'active')),
            ],
            options={
                'ordering': ['interestName'],
                'db_table': 'volunteerInterests',
                'verbose_name_plural': 'Interest Type',
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
                ('volStatus', models.CharField(db_column=b'volStatus', default=b'pending', choices=[(b'pending', b'Pending'), (b'approved', b'Approved')], max_length=15, blank=True, null=True, verbose_name=b'Volunteer Status')),
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
            name='VolunteerToFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='nsavolunteer.FamilyProfile')),
                ('person', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Volunteer To Family',
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
        migrations.AlterUniqueTogether(
            name='volunteertofamily',
            unique_together=set([('person', 'group')]),
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='volunteerType',
            field=models.ForeignKey(db_column=b'volunteerType', blank=True, to='nsavolunteer.VolunteerType', null=True, verbose_name=b'Volunteer Type'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='studenttofamily',
            unique_together=set([('student', 'group')]),
        ),
        migrations.AddField(
            model_name='historicalvolunteerprofile',
            name='volunteerType',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'volunteerType', db_constraint=False, blank=True, to='nsavolunteer.VolunteerType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalstudenttofamily',
            name='student',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='nsavolunteer.Student', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyprofile',
            name='students',
            field=models.ManyToManyField(to='nsavolunteer.Student', verbose_name=b'Students', through='nsavolunteer.StudentToFamily'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyprofile',
            name='volunteers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Volunteers', through='nsavolunteer.VolunteerToFamily'),
            preserve_default=True,
        ),
    ]
