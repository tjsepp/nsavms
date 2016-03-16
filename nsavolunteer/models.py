from django.db import models
from django.conf import settings
from authtools.models import AbstractEmailUser
from simple_history.models import HistoricalRecords
from authtools.models import User
from django.db.models.signals import post_save,pre_delete
from nsaSchool.models import GradeLevel,Teachers,SchoolYear
from nsaEvents.models import NsaEvents
from django.db.models import Sum
from collections import defaultdict
from itertools import chain

STORES = (('King Soopers','King Soopers'),('Safeway','Safeway'))
VOLSTATUS = (('pending','Pending'),('approved','Approved'))
GRADELEVEL = (('0','Kindergarten'),('1','1st Grade'),('2','2nd Grade'),('3','3rd Grade'),('4','4th Grade'),
              ('5','5th Grade'),('6','6th Grade'),('7','7th Grade'),('8','8th Grade'))

TRAFFICDUTY = (('am','Drop-off'),('pm','Pick-up'))


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

    def fullName(self):
        return '%s %s' %(self.firstName,self.lastName)
    fullName.short_description = 'Full Name'

    def getFamilies(self):
        url = '' #add the url to the main family page
        fams = FamilyProfile.objects.filter(famvolunteers = self.linkedUserAccount)
        if fams:
            famlist1 =[]
            for fam in fams:
                link = "<a href='familyprofile/%s' target='_blank'>%s</a>" %(fam.familyProfileId,fam.familyName)
                famlist1.append(link)
            famList = '%s' % ",".join([famlink for famlink in famlist1])
        else:
            famList = 'Not tied to family'
        return famList

    def save(self, force_insert=False,force_update=False, using=None):
        if not self.volunteerProfileID:
            self.firstName = self.linkedUserAccount.name.split(' ',1)[0]
            self.lastName = self.linkedUserAccount.name.split(' ',1)[1]
        super(VolunteerProfile,self).save(force_insert, force_update)

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            VolunteerProfile.objects.create(linkedUserAccount=instance)
    post_save.connect(create_user_profile, sender=User)

    @property
    def historical_volunteer_data(self):
        curUser = User.objects.select_related('volunteerhours_set','rewardCardValue','family').get(pk=self.linkedUserAccount.id)
        rhh = curUser.rewardCardValue.values('schoolYear__schoolYear').annotate(total=Sum('volunteerHours')).order_by('-schoolYear')
        vhh = curUser.volunteerhours_set.values('schoolYear__schoolYear').annotate(total=Sum('volunteerHours')).order_by('-schoolYear')
        tdu = curUser.trafficDutyUser.values('schoolYear__schoolYear').annotate(total=Sum('volunteerHours')).order_by('-schoolYear')
        cb = chain(rhh,vhh,tdu)
        io =[]
        for x in cb:
             io.append(x)
        c = defaultdict(int)
        for d in io:
            c[d['schoolYear__schoolYear']] += d['total']
        histHours =  [{'schoolYear': schoolYear__schoolYear, 'total': total} for schoolYear__schoolYear, total in c.items()]
        return histHours

    class Meta:
        verbose_name_plural='Volunteer Profile'
        db_table = 'volunteerProfile'
        ordering = ['linkedUserAccount__name']
        permissions = (
            ("is_avc", "Is AVC"),
            ("is_volunteer_manager", "Is Volunteer Manager"),
            ("is_traffic_manager", "Is Traffic Manager")
        )


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
    students = models.ManyToManyField(Student,verbose_name='Students',blank=True,through='StudentToFamily')
    active =  models.BooleanField(verbose_name='active',db_column='active',default=True)
    history = HistoricalRecords()

    @property
    def listVolunteers(self):
        vols = self.famvolunteers.all()
        volList = '%s' % ",".join([vol.name for vol in vols])
        return volList

    @property
    def listStudents(self):
        stus = self.students.all()
        stuList = '%s' % ",".join([stu.studentFirstName for stu in stus])
        return stuList

    @property
    def totalCurrentVolunteerHours(self):
      curYear = SchoolYear.objects.filter(currentYear=1)
      hours = VolunteerHours.objects.select_related('family').filter(family=self.familyProfileId).filter(schoolYear=curYear) \
              .aggregate(total=Sum('volunteerHours'))
      if hours['total']:
          total = hours['total']
      else:
          total = 0
      return total

    @property
    def totalCurrentRewardCardHours(self):
      curYear = SchoolYear.objects.filter(currentYear=1)
      hours = RewardCardUsage.objects.select_related('family').filter(linkedFamily_id=self.familyProfileId).filter(schoolYear =curYear).aggregate(total=Sum('volunteerHours'))
      if hours['total']:
          total = hours['total']
      else:
          total = 0
      return total

    @property
    def totalCurrentParkingDutyHours(self):
      curYear = SchoolYear.objects.filter(currentYear=1)
      hours = TrafficDuty.objects.select_related('family').filter(linkedFamily_id=self.familyProfileId).filter(schoolYear =curYear).aggregate(total=Sum('volunteerHours'))
      if hours['total']:
          total = hours['total']
      else:
          total = 0
      return total

    @property
    def totalCurrentHours(self):
      hours =  self.totalCurrentVolunteerHours + self.totalCurrentRewardCardHours+self.totalCurrentParkingDutyHours
      return hours

    def __unicode__(self):
        return self.familyName


    class Meta:
        verbose_name_plural='Family Profile'
        db_table = 'familyProfile'


'''
class VolunteerToFamily(TimeStampedModel):
    person = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(FamilyProfile)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Volunteer To Family'
        unique_together = ("person", "group")

    def __unicode__(self):
        return '%s (%s)' %(self.person.name,self.group)
'''

class VolunteerHoursManager(models.Manager):
    def current_year(self):
        curYear = SchoolYear.objects.get(currentYear = 1)
        return self.get_queryset().filter(schoolYear = curYear)



class VolunteerHours(TimeStampedModel):
    volunteerHoursId = models.AutoField(primary_key=True,db_column='volunteerHoursId',verbose_name='Volunteer Hours Id')
    event = models.ForeignKey(NsaEvents,db_column='event',null=True, blank=True, verbose_name='Event', related_name='volHours')
    eventDate = models.DateField(db_column='volunteerDate', verbose_name='Volunteer Date', blank=True, null=True)
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer', verbose_name='volunteer')
    family = models.ForeignKey('FamilyProfile',db_column='family', verbose_name='Family',help_text="Select Family to log hours for.")
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Volunteer Hours')
    approved = models.BooleanField(db_column='approved', default=False,verbose_name='Approved')
    objects = VolunteerHoursManager()

    def __unicode__(self):
        return "%s's %s on %s" %(self.volunteer.name, self.event, self.eventDate)


    def save(self, force_insert=False,force_update=False, using=None):
        if self.event.autoApprove==True:
            self.approved = True
        super(VolunteerHours,self).save(force_insert, force_update)


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
    family = models.ForeignKey('FamilyProfile',db_column='family', verbose_name='Family', null=True)
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
    linkedFamily = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name='family',blank=True,null=True,related_name='rewardCardFamilyLink')
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
        if not self.linkedFamily:
            cardfamily = RewardCardUsers.objects.get(customerCardNumber = self.customerCardNumber)
            self.linkedFamily = cardUser.family
        super(RewardCardUsage,self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural='Reward Card Purchase Data'
        db_table = 'rewardCardData'
        ordering = ['refillDate']


class TrafficDuty(TimeStampedModel):
    trafficDutyId= models.AutoField(primary_key=True,db_column='ParkingDutyId',verbose_name='Parking Duty ID')
    trafficDutyDate = models.DateField(db_column='parkingDutyDate', verbose_name='Parking Duty Date', null=True, blank=True)
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)
    volunteerId = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer',verbose_name='Volunteer', blank=True, null=True, related_name='trafficDutyUser')
    linkedFamily = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name='family',blank=True,null=True,related_name='parkingDutyFamily')
    trafficDutyType =models.CharField(max_length=25,db_column='store',verbose_name='Duty Type',null=True,blank=False,choices=TRAFFICDUTY)
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Volunteer Hours')

    def __unicode__(self):
        return '%s - %s' %(self.volunteerId.name,self.trafficDutyDate)


    class Meta:
        verbose_name_plural='Traffic Duty'
        db_table = 'trafficDuty'
        ordering = ['trafficDutyDate']

    def save(self, force_insert=False,force_update=False, using=None):
        if not self.volunteerHours:
            if self.trafficDutyType == 'am':
                volTime = 1
            elif self.trafficDutyType =='pm':
                volTime = 1.5
            else:
                volTime = 0
            self.volunteerHours = volTime
        super(TrafficDuty,self).save(force_insert, force_update)