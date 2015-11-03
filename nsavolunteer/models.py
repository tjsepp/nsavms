from django.db import models
from django.conf import settings
from authtools.models import AbstractEmailUser
from simple_history.models import HistoricalRecords
from organizations.models import Organization, OrganizationUser
from organizations.base import (OrganizationBase, OrganizationUserBase,
        OrganizationOwnerBase)
from tinymce import models as tinymce_models
from authtools.models import User
from django.db.models.signals import post_save,pre_delete


STORES = (('King Soopers','King Soopers'),('Safeway','Safeway'))


class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VolunteerNews(TimeStampedModel):
    '''
    This class allows users to add news to the volunteer site. It is aided by tinyMCE which allows for specific formatting
    '''
    newsID = models.AutoField(primary_key=True,db_column='newsID',verbose_name='VolunteerNewsId')
    headline = models.CharField(max_length=250,db_column='title',verbose_name='News Title', null=True, blank=False, default=None)
    #body = models.TextField(verbose_name='News Body', db_column='body', null=True, blank=False)
    body = tinymce_models.HTMLField(verbose_name='News Body', db_column='body', null=True, blank=False)
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
    '''
    This class contains the volunteer profile. It is related one:one with a user. It allows for expanded information on the user
    model.
    '''
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
    '''
    def deleteUserProfile(sender, instance,using=None,**kwargs):
        recs = VolunteerProfile.history.filter(instance)
        for rec in recs:
            rec.delete()
        VolunteerProfile.delete(instance)
    pre_delete.connect(deleteUserProfile, sender=User)
    '''
    def fullName(self):
        return '%s %s' %(self.firstName,self.lastName)
    fullName.short_description = 'Full Name'

    def save(self, force_insert=False,force_update=False, using=None):
        if not self.volunteerProfileID:
            self.firstName = self.linkedUserAccount.name.split()[0]
            self.lastName = self.linkedUserAccount.name.split()[1]
        super(VolunteerProfile,self).save(force_insert, force_update)

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            VolunteerProfile.objects.create(linkedUserAccount=instance)
    post_save.connect(create_user_profile, sender=User)

    class Meta:
        verbose_name_plural='Volunteer Profile'
        db_table = 'volunteerProfile'
        ordering = ['linkedUserAccount__name']


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





class Student(TimeStampedModel):
    '''
    This model will store students. This will be linked to the family model to allow us to manage
    a historical perspective of students.
    '''
    studentId = models.AutoField(primary_key=True,db_column='studentId',verbose_name='StudentId')
    studentName = models.CharField(max_length=100,db_column='studentName',verbose_name='Student Name',null=True,blank=False)
    activeStatus = models.BooleanField(verbose_name='Active Status',default=True,db_column='activeStatus')
    #teacher
    #grade
    history = HistoricalRecords()

    def __unicode__(self):
        return self.studentName

    class Meta:
        verbose_name_plural = 'Students'
        db_table='Students'
        ordering =['studentName']

class StudentToFamily(TimeStampedModel):
    student = models.ForeignKey(Student)
    group = models.ForeignKey('FamilyProfile')
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Student To Family'
        db_table = 'studentToFamily'
        ordering = ['student']
        unique_together = ("student", "group")

    def __unicode__(self):
        return '%s (%s)' %(self.student,self.group)


class FamilyProfile(TimeStampedModel):
    '''
    This creates a family/organization that allows for multiple users to be added. This will be the main unit used to
    roll up all data to a family level.
    '''
    familyProfileId = models.AutoField(primary_key=True,db_column='FamilyProfileId',verbose_name='Family Profile Id')
    familyName =  models.CharField(max_length=50,db_column='familyName',verbose_name='Family Name', null=True, blank=True, default=None)
    streetAddress = models.CharField(db_column='streetAddress', max_length=200, null=True,blank=True,verbose_name='Street Address')
    city = models.CharField(db_column='city', max_length=50, null=True,blank=True,verbose_name='city')
    zip = models.CharField(db_column='zip', max_length=15, null=True,blank=True,verbose_name='zip')
    homePhone = models.CharField(max_length=15,db_column='homePhone',verbose_name='Home Phone', null=True, blank=True, default=None)
    specialInfo = models.TextField(verbose_name='Volunteer Note', db_column='VolunteerNote', null=True, blank=True)
    inactiveDate = models.DateField(verbose_name='Inactive Date',db_column='inactiveDate',null=True,blank=True)
    volunteers = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name='Volunteers',through='VolunteerToFamily')
    students = models.ManyToManyField(Student,verbose_name='Students',through='StudentToFamily')
    active =  models.BooleanField(verbose_name='active',db_column='active',default=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.familyName


    class Meta:
        verbose_name_plural='Family Profile'
        db_table = 'familyProfile'


class VolunteerToFamily(TimeStampedModel):
    person = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(FamilyProfile)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Volunteer To Family'
        unique_together = ("person", "group")

    def __unicode__(self):
        return '%s (%s)' %(self.person.name,self.group)



class RewardCardUsers(TimeStampedModel):
    '''
    This model will store the King Soopers & Safeway rewards card information
    This will link values back to the user allowing the system to aggregate the information on the user level
    '''
    RewardCardId = models.AutoField(primary_key=True,db_column='rewardCardId',verbose_name='Reward Card ID')
    linkedUser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rewardCardUser',verbose_name='LinkedUser',db_column='linkedUser')
    storeName = models.CharField(max_length=25,db_column='store',verbose_name='Store',null=True,blank=False,choices=STORES)
    customerCardNumber = models.CharField(max_length=50, db_column='cardNumber',verbose_name='Card Number',blank=False,null=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.linkedUser.name

    class Meta:
        verbose_name_plural = 'Reward Card User Information'
        db_table = 'rewardCardUserInformation'
        ordering = ['dateCreated']





