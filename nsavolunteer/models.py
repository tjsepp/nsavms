from django.db import models
from django.conf import settings
from authtools.models import AbstractEmailUser
from simple_history.models import HistoricalRecords
from authtools.models import User
from django.db.models.signals import post_save,pre_delete
from nsaSchool.models import GradeLevel,Teachers,SchoolYear
from nsaEvents.models import NsaEvents

STORES = (('King Soopers','King Soopers'),('Safeway','Safeway'))
VOLSTATUS = (('pending','Pending'),('approved','Approved'))
GRADELEVEL = (('0','Kindergarten'),('1','1st Grade'),('2','2nd Grade'),('3','3rd Grade'),('4','4th Grade'),
              ('5','5th Grade'),('6','6th Grade'),('7','7th Grade'),('8','8th Grade'))


class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    volStatus = models.CharField(max_length=15,db_column='volStatus',verbose_name='Volunteer Status',null=True,blank=True,choices=VOLSTATUS,default='pending')
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

    def getFamilies(self):
        url = '' #add the url to the main family page
        fams = FamilyProfile.objects.filter(volunteers = self.linkedUserAccount)
        if fams:
            famlist1 =[]
            for fam in fams:
                link = "<a href='user_profile%s' target='_blank'>%s</a>" %(fam.familyProfileId,fam.familyName)
                famlist1.append(link)
            famList = '%s' % ",".join([famlink for famlink in famlist1])
        else:
            famList = 'Not tied to family'
        return famList

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
    studentFirstName = models.CharField(max_length=100,db_column='studentFirstName',verbose_name='Students First Name',null=True,blank=False)
    studentLastName = models.CharField(max_length=100,db_column='studentLastName',verbose_name='Students Last Name',null=True,blank=False)
    activeStatus = models.BooleanField(verbose_name='Active Status',default=True,db_column='activeStatus')
    teacher= models.ForeignKey(Teachers,db_column='teacher',null=True, blank=True,on_delete=models.SET_NULL)
    grade = models.ForeignKey(GradeLevel,db_column='gradeLevel',verbose_name='Grade Level', null=True, blank=True)
    history = HistoricalRecords()

    def getFullStudentName(self):
        return '%s %s' %(self.studentFirstName, self.studentLastName)

    def __unicode__(self):
        return self.getFullStudentName()

    class Meta:
        verbose_name_plural = 'Students'
        db_table='students'
        ordering =['studentLastName']


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
    familyName =  models.CharField(max_length=50,db_column='familyName',verbose_name='Family Name', null=True, blank=False, default=None)
    streetAddress = models.CharField(db_column='streetAddress', max_length=200, null=True,blank=True,verbose_name='Street Address')
    city = models.CharField(db_column='city', max_length=50, null=True,blank=True,verbose_name='city')
    zip = models.CharField(db_column='zip', max_length=15, null=True,blank=True,verbose_name='zip')
    homePhone = models.CharField(max_length=15,db_column='homePhone',verbose_name='Home Phone', null=True, blank=True, default=None)
    specialInfo = models.TextField(verbose_name='Family Note', db_column='VolunteerNote', null=True, blank=True)
    inactiveDate = models.DateField(verbose_name='Inactive Date',db_column='inactiveDate',null=True,blank=True)
    famvolunteers = models.ManyToManyField(User,verbose_name='Volunteers',db_table='familyVolunteers',blank=True,related_name='family')
    #volunteers = models.ManyToManyField(User,verbose_name='Volunteers',through='VolunteerToFamily', related_name='family')
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


class VolunteerHoursManager(models.Manager):
    def current_year(self):
        curYear = SchoolYear.objects.get(currentYear = 1)
        return self.get_queryset().filter(schoolYear = curYear)



class VolunteerHours(TimeStampedModel):
    volunteerHoursId = models.AutoField(primary_key=True,db_column='volunteerHoursId',verbose_name='Volunteer Hours Id')
    event = models.ForeignKey(NsaEvents,db_column='event',null=True, blank=True, verbose_name='Event', related_name='volHours')
    eventDate = models.DateField(db_column='volunteerDate', verbose_name='Volunteer Date', blank=True, null=True)
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer', verbose_name='volunteer')
    family = models.ForeignKey('FamilyProfile',db_column='family', verbose_name='Family')
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Volunteer Hours')
    objects = VolunteerHoursManager()


    def __unicode__(self):
        return "%s's %s on %s" %(self.volunteer.name, self.event, self.eventDate)



    class Meta:
        verbose_name_plural = 'Volunteer Hours'
        db_table = 'volunteerHours'
        ordering = ['eventDate']


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


class RewardCardUsage(TimeStampedModel):
    '''
    This model will contain the monthly values allowing the system to tabulate the total money
    spent on reward refils/repurchases
    '''
    rewardCardusageId= models.AutoField(primary_key=True,db_column='rewardCardUsageId',verbose_name='Reward Card Usage ID')
    customerCardNumber = models.CharField(max_length=50, db_column='customerCardNumber',verbose_name='Card Number',blank=False,null=True)
    volunteerId = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer',verbose_name='Volunteer', blank=True, null=True, related_name='rewardCardValue')
    refillDate = models.DateField(db_column='refillDate', verbose_name='Refill Date', null=True, blank=True)
    refillValue = models.DecimalField(db_column='refillValue',verbose_name='Refill Value',max_digits=8, decimal_places=2)
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Volunteer Hours')
    storeName = models.CharField(max_length=25,db_column='store',verbose_name='Store',null=True,blank=False,choices=STORES)
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)


    def __unicode__(self):
        return '%s - %s - $%0.2f' %(self.volunteerId.name,self.refillDate,self.refillValue)

    def volunteer_Hours(self):
        return self.refillValue/100

    def save(self, force_insert=False,force_update=False, using=None):
        if not self.volunteerId:
            cardUser = RewardCardUsers.objects.get(customerCardNumber = self.customerCardNumber)
            self.volunteerId = cardUser.linkedUser
        if not self.volunteerHours:
            self.volunteerHours = self.volunteer_Hours()
        super(RewardCardUsage,self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural='Reward Card Purchase Data'
        db_table = 'rewardCardData'
        ordering = ['refillDate']

