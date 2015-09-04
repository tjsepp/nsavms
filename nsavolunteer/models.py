from django.db import models
from django.conf import settings
from authtools.models import AbstractEmailUser
from simple_history.models import HistoricalRecords
from organizations.models import Organization, OrganizationUser
from organizations.base import (OrganizationBase, OrganizationUserBase,
        OrganizationOwnerBase)

class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VolunteerNews(TimeStampedModel):
    newsID = models.AutoField(primary_key=True,db_column='newsID',verbose_name='VolunteerNewsId')
    headline = models.CharField(max_length=250,db_column='title',verbose_name='News Title', null=True, blank=False, default=None)
    body = models.TextField(verbose_name='News Body', db_column='body', null=True, blank=False)
    newsEndDate = models.DateField(verbose_name ='NewsEndDate', db_column='enddate', null=True, blank=False, help_text='For indefinite news, enter 1/1/2900')
    topPriority = models.BooleanField(verbose_name='Top priority', db_column='prioriyy', default=False)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.headline

    class Meta:
        verbose_name_plural='Volunteer News'
        db_table = 'volunteerNews'
        ordering = ['dateCreated']

class VolunteerProfile(TimeStampedModel):
    volunteerProfileID =  models.AutoField(primary_key=True,db_column='volunteerProfileId',verbose_name='Volunteer Profile Id')
    firstName = models.CharField(db_column='firstName', max_length=200, null=True,blank=True,verbose_name='First Name')
    lastName = models.CharField(db_column='lastName', max_length=200, null=True,blank=True,verbose_name='Last Name')
    linkedUserAccount = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='linkedUser')
    volunteerType = models.ForeignKey('VolunteerType',null=True,blank=True,db_column='volunteerType',verbose_name='Volunteer Type')
    cellPhone =models.CharField(max_length=15,db_column='cellPhone',verbose_name='cell Phone', null=True, blank=True, default=None)
    interest = models.ManyToManyField('nsavolunteer.VolunteerInterests',db_table ='profileToInterest',verbose_name='Volunteer Interests', null=True, blank =True, related_name='profile_interest')
    doNotEmail = models.BooleanField(verbose_name='Do Not Email',db_column='emailOptOut',default=False)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.linkedUserAccount.name

    def fullName(self):
        return '%s %s' %(self.firstName,self.lastName)
    fullName.short_description = 'Full Name'

    def get_interests(self):
        from itertools import chain
        if self.interest:
            ints = self.interest.all()
        return '%s' % " , ".join([int.interestName for int in ints])


    def save(self, force_insert=False,force_update=False):
        if not self.volunteerProfileID:
            self.firstName = self.linkedUserAccount.name.split()[0]
            self.lastName = self.linkedUserAccount.name.split()[1]
        super(VolunteerProfile,self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural='Volunteer Profile'
        db_table = 'volunteerProfile'
        ordering = ['linkedUserAccount__name']


class FamilyProfile(OrganizationBase):
    #familyProfileId = models.AutoField(primary_key=True,db_column='FamilyProfileId',verbose_name='Family Profile Id')
    streetAddress = models.CharField(db_column='streetAddress', max_length=200, null=True,blank=True,verbose_name='Street Address')
    city = models.CharField(db_column='city', max_length=50, null=True,blank=True,verbose_name='city')
    zip = models.CharField(db_column='zip', max_length=15, null=True,blank=True,verbose_name='zip')
    homePhone = models.CharField(max_length=15,db_column='homePhone',verbose_name='Home Phone', null=True, blank=True, default=None)
    specialInfo = models.TextField(verbose_name='Volunteer Note', db_column='VolunteerNote', null=True, blank=True)
    inactiveDate = models.DateField(verbose_name='Inactive Date',db_column='inactiveDate',null=True,blank=True)
    active =  models.BooleanField(verbose_name='active',db_column='active',default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural='Family Profile'
        db_table = 'familyProfile'





class FamilyToUser(OrganizationUserBase):
    organization = models.ForeignKey(FamilyProfile,verbose_name='Related Family')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='User')

    class Meta:
        verbose_name = 'User to Family'
        verbose_name_plural='Family to User'
        db_table = 'familytouser'

class FamilyProfileOwner(OrganizationOwnerBase):
    class Meta:
        verbose_name_plural='Family Profile Owner'
        db_table = 'familyProfileowner'


class VolunteerType(TimeStampedModel):
    '''
    This class contains the different type of volunteers
    '''
    volunteerTypeId = models.AutoField(primary_key=True,db_column='volunteerTypeId',verbose_name='Volunteer Type ID')
    volunteerType =  models.CharField(db_column='volunteerType', max_length=200, null=True,verbose_name='Volunteer Type')
    description = models.TextField(verbose_name='Volunteer Type Description', db_column='volTypeDescription', null=True, blank=True)
    history=HistoricalRecords()

    def __unicode__(self):
        return self.volunteerType

    class Meta:
        verbose_name_plural='Volunteer Type'
        db_table = 'volunteerType'
        ordering = ['volunteerType']


class VolunteerInterests(TimeStampedModel):
    '''
    This class contains the interest types. It is used to identify what activities families will be interested in.
    '''
    interestId = models.AutoField(primary_key=True,db_column='interestId',verbose_name='Interest Id')
    interestName = models.CharField(db_column='interestName', max_length=200, null=True,verbose_name='Interest')
    description = models.TextField(verbose_name='Interest Description', db_column='interestDescription', null=True, blank=True)
    active = models.BooleanField(verbose_name='Active', db_column='active',default=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.interestName

    class Meta:
        verbose_name_plural='Interest Type'
        db_table = 'volunteerInterests'
        ordering = ['interestName']