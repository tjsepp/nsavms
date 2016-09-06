from django.db import models
from django.conf import settings
from authtools.models import AbstractEmailUser
from simple_history.models import HistoricalRecords
from authtools.models import User
from django.db.models.signals import post_save,pre_delete
from nsaSchool.models import GradeLevel,Teachers,SchoolYear
from nsaEvents.models import NsaEvents, EventTasks
from django.db.models import Sum, Count
from collections import defaultdict
from itertools import chain


STORES = (('King Soopers','King Soopers'),('Safeway','Safeway'))
VOLSTATUS = (('pending','Pending'),('approved','Approved'))
GRADELEVEL = (('0','Kindergarten'),('1','1st Grade'),('2','2nd Grade'),('3','3rd Grade'),('4','4th Grade'),
              ('5','5th Grade'),('6','6th Grade'),('7','7th Grade'),('8','8th Grade'))

TRAFFICDUTY = (('am','Drop-off'),('pm','Pick-up'))
TRAFFICDUTY_INT=((0,'0'),(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'))

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
    linkedUserAccount = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='linkedUser',db_index=True)
    volunteerType = models.ForeignKey('VolunteerType',null=True,blank=True,db_column='volunteerType',verbose_name='Volunteer Type')
    cellPhone =models.CharField(max_length=15,db_column='cellPhone',verbose_name='cell Phone', null=True, blank=True, default=None)
    volStatus = models.CharField(max_length=15,db_column='volStatus',verbose_name='Volunteer Status',null=True,blank=True,choices=VOLSTATUS,default='pending')
    interest = models.ManyToManyField('nsavolunteer.VolunteerInterests',db_table ='profileToInterest',verbose_name='Volunteer Interests', blank =True, related_name='profile_interest')
    doNotEmail = models.BooleanField(verbose_name='Do Not Email',db_column='emailOptOut',default=False)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.linkedUserAccount.name

    def fullName(self):
        if 'AVC' in  self.linkedUserAccount.groups.values_list('name', flat=True):
            return '%s %s (AVC)' %(self.firstName,self.lastName)
        else:
            return '%s %s' %(self.firstName,self.lastName)
    fullName.short_description = 'Full Name'

    def getFamilies(self):
        url = '' #add the url to the main family page
        fams = FamilyProfile.objects.select_related('famvolunteers').filter(famvolunteers = self.linkedUserAccount)
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
        curUser = User.objects.prefetch_related('linkedUser__linkedUserAccount__volunteerhours_set',
                                                'linkedUser__linkedUserAccount__rewardCardValue',
                                                'linkedUser__linkedUserAccount__family').get(pk=self.linkedUserAccount.id)
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

    @property
    def currentVolunteerData(self):
        volunteerEvents = VolunteerHours.objects.select_related('event','family','volunteer').filter(schoolYear = SchoolYear.objects.get(currentYear = 1)).\
            filter(volunteer = self.volunteerProfileID)
        return volunteerEvents

    @property
    def currentTrafficDutyData(self):
        trafficDuty = TrafficDuty.objects.filter(schoolYear = SchoolYear.objects.get(currentYear = 1)).\
            filter(volunteerId = self.volunteerProfileID)
        return trafficDuty

    @property
    def currentRewardCardData(self):
        rewardCard = RewardCardUsage.objects.filter(schoolYear = SchoolYear.objects.get(currentYear = 1)).\
            filter(volunteerId = self.volunteerProfileID)
        return rewardCard

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
    activeStatus = models.BooleanField(verbose_name='Current Student',default=True,db_column='activeStatus')
    teacher= models.ForeignKey(Teachers,db_column='teacher',null=True, blank=True,on_delete=models.SET_NULL, related_name='students')
    grade = models.ForeignKey(GradeLevel,db_column='gradeLevel',verbose_name='Grade Level', null=True, blank=True)
    history = HistoricalRecords()

    def getFullStudentName(self):
        return '%s %s' %(self.studentFirstName, self.studentLastName)

    def newYear(self):
        newGrade = GradeLevel.objects.get(gradeOrder=self.grade.gradeOrder+1)
        self.grade=newGrade
        self.teacher=None
        if newGrade.gradeOrder>=9:
            self.activeStatus=False
        self.save()



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
    familyName =  models.CharField(max_length=50,db_column='familyName',verbose_name='Family Name', null=True, blank=False, default=None,db_index=True)
    streetAddress = models.CharField(db_column='streetAddress', max_length=200, null=True,blank=True,verbose_name='Street Address')
    city = models.CharField(db_column='city', max_length=50, null=True,blank=True,verbose_name='city')
    zip = models.CharField(db_column='zip', max_length=15, null=True,blank=True,verbose_name='zip')
    homePhone = models.CharField(max_length=15,db_column='homePhone',verbose_name='Home Phone', null=True, blank=True, default=None)
    specialInfo = models.TextField(verbose_name='Family Note', db_column='VolunteerNote', null=True, blank=True)
    trafficRequirement = models.IntegerField(verbose_name='Traffic Requirement', db_column='trafficReq',null=True,blank=True,default=6)
    volunteerRequirement = models.IntegerField(verbose_name='Volunteer Requirement', db_column='volunteerReq',null=True,blank=True,default=40)
    inactiveDate = models.DateField(verbose_name='Inactive Date',db_column='inactiveDate',null=True,blank=True)
    famvolunteers = models.ManyToManyField(User,verbose_name='Volunteers',db_table='familyVolunteers',blank=True,related_name='family')
    #volunteers = models.ManyToManyField(User,verbose_name='Volunteers',through='VolunteerToFamily', related_name='family')
    students = models.ManyToManyField(Student,verbose_name='Students',blank=True,through='StudentToFamily')
    active =  models.BooleanField(verbose_name='active',db_column='active',default=True)
    history = HistoricalRecords()



    @property
    def listVolunteers(self):
        vols = self.famvolunteers.all()
        volList = '%s' % ",".join([vol.linkedUser.fullName() for vol in vols])
        return volList

    @property
    def listStudents(self):
        stus = self.students.all()
        stuList = '%s' % ",".join([stu.studentFirstName for stu in stus])
        return stuList

    @property
    def totalCurrentHours(self):
      hours =  FamilyAggHours.objects.filter(family=self).filter(schoolYear=SchoolYear.objects.filter(currentYear=1))
      if hours:
          total = hours[0].totalVolHours
      else:
          total = 0
      return total

    @property
    def totalCurrentTrafficDutyCount(self):
      hours =  FamilyAggHours.objects.filter(family=self).filter(schoolYear=SchoolYear.objects.filter(currentYear=1))
      if hours:
          total = hours[0].trafficDutyCount
      else:
          total = 0
      return total

    def deactivateWholeFamily(self):
        for vol in self.famvolunteers.all():
            vol.is_active=False
            vol.save()
        for student in self.students.all():
            student.activeStatus = False
            student.save()

    def __unicode__(self):
        return self.familyName


    class Meta:
        verbose_name_plural='Family Profile'
        db_table = 'familyProfile'


class VolunteerHoursManager(models.Manager):
    def current_year(self):
        curYear = SchoolYear.objects.get(currentYear = 1)
        return self.get_queryset().filter(schoolYear = curYear)


class VolunteerHours(TimeStampedModel):
    volunteerHoursId = models.AutoField(primary_key=True,db_column='volunteerHoursId',verbose_name='Volunteer Hours Id')
    event = models.ForeignKey(NsaEvents,db_column='event',null=True, blank=False, verbose_name='Event', related_name='volHours')
    task = models.CharField(max_length=100,db_column='task',null=True,blank=True,verbose_name='task')
    eventDate = models.DateField(db_column='volunteerDate', verbose_name='Volunteer Date', blank=False, null=True,db_index=True)
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer', verbose_name='volunteer',db_index=True)
    family = models.ForeignKey('FamilyProfile',db_column='family', verbose_name='Family',help_text="Select Family to log hours for.",db_index=True)
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=False,verbose_name='Volunteer Hours')
    approved = models.BooleanField(db_column='approved', default=False,verbose_name='Approved')
    objects = VolunteerHoursManager()

    def __unicode__(self):
        return "%s's %s on %s" %(self.volunteer.name, self.event, self.eventDate)

    def save(self, *args, **kwargs):
        if self.event.autoApprove==True:
            self.approved = True

        if self.pk:
            #if the volunteerHours record already exists
            #get saved record
            origRecord = VolunteerHours.objects.get(pk=self.pk)
            #get hours and approval saved from original volunteerHours save
            origHours = origRecord.volunteerHours
            hourChange = origHours != self.volunteerHours #this is the test to see if the hours changed from the last save
            origapproval = origRecord.approved
            approvalChange = origapproval !=self.approved #This is the test to see if the approval changed from the last save
            familyChange = origRecord.family !=self.family
            print familyChange


            if not origapproval: #if the original record was never approved, make it a zero as to not effect the calculations below
                origHours = 0

            #get or create new record
            p, created = FamilyAggHours.objects.get_or_create(family = self.family, schoolYear = self.schoolYear)

            if not created: #if a new family agg record wasn't created
                summed_hours = p.totalVolHours #assign the summed_hours variable

                if hourChange and approvalChange: #check if both the hours and approval changed
                    if not origRecord.approved:
                        #if the saved record wasn't approved, theres no need to back out data
                        summed_hours = p.totalVolHours
                    else:
                        summed_hours = p.totalVolHours - origHours #backs out the original hours
                    if self.approved: #if the new/updated record is approved, add it to the sum.
                        summed_hours = summed_hours + self.volunteerHours

                elif hourChange:
                    if self.approved:
                        summed_hours = summed_hours - origHours + self.volunteerHours
                    else:
                        summed_hours = summed_hours - origHours

                elif approvalChange:
                    if not self.approved:
                        summed_hours = summed_hours - origHours
                    else:
                        summed_hours = summed_hours - origHours + self.volunteerHours

                else:
                    if self.approved:
                        summed_hours = summed_hours

                if summed_hours <0:
                    summed_hours = 0

                p.totalVolHours = summed_hours
                p.save()

                if familyChange: #if there is a change in families - remove hours from old family and add to the new family
                    oldFam = FamilyAggHours.objects.get(family=origRecord.family, schoolYear=origRecord.schoolYear)
                    oldFam.totalVolHours = oldFam.totalVolHours - self.volunteerHours
                    oldFam.save()
                    #add hours to new family
                    p.totalVolHours = summed_hours + self.volunteerHours
                    p.save()

            if created: #if a new family Sum record is created then just add the hours.
                if self.approved:
                    p.totalVolHours = self.volunteerHours
                p.save()

                #if there is a change in family, back out data from old family
                if familyChange: #if there is a change in families - remove hours from old family and add to the new family
                    oldFam = FamilyAggHours.objects.get(family=origRecord.family, schoolYear=origRecord.schoolYear)
                    oldFam.totalVolHours = oldFam.totalVolHours - self.volunteerHours
                    oldFam.save()
        else:
            p, created = FamilyAggHours.objects.get_or_create(family = self.family, schoolYear = self.schoolYear)
            if self.approved:
                    p.totalVolHours = p.totalVolHours+self.volunteerHours
            p.save()
        super(VolunteerHours, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        p = FamilyAggHours.objects.get(family = self.family, schoolYear = self.schoolYear)
        if self.approved:
            hoursToRemove = p.totalVolHours - self.volunteerHours
            p.totalVolHours = hoursToRemove
        p.save()
        super(VolunteerHours, self).delete(*args, **kwargs)

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
    linkedUser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rewardCardUser',verbose_name='LinkedUser',db_column='linkedUser',db_index=True)
    family = models.ForeignKey('FamilyProfile',db_column='family', verbose_name='Family', null=True,db_index=True)
    storeName = models.CharField(max_length=25,db_column='store',verbose_name='Store',null=True,blank=False,choices=STORES)
    customerCardNumber = models.CharField(max_length=50, db_column='cardNumber',verbose_name='Card Number',blank=False,null=True)
    active = models.BooleanField(verbose_name='active',db_column='active',default=True)
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
    customerCardNumber = models.CharField(max_length=50, db_column='customerCardNumber',verbose_name='Card Number',blank=False,null=True,db_index=True)
    volunteerId = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer',verbose_name='Volunteer', blank=True, null=True, related_name='rewardCardValue',db_index=True)
    linkedFamily = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name='family',blank=True,null=True,related_name='rewardCardFamilyLink',db_index=True)
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

class Traffic_Duty(TimeStampedModel):
    ''' This is the new traffic duty class to allow for weekly input vs. daily observations.
    '''
    trafficDutyId= models.AutoField(primary_key=True,db_column='TrafficDutyId',verbose_name='Traffic Duty ID')
    volunteerId = models.ForeignKey(settings.AUTH_USER_MODEL,db_column='volunteer',verbose_name='Volunteer', blank=True, null=True, related_name='trafficDuty_User',db_index=True)
    linkedFamily = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name='Family',blank=False,null=True,related_name='trafficDutyFamily',db_index=True)
    schoolYear = models.ForeignKey(SchoolYear, db_column='SchoolYear',verbose_name='School Year', null=True,blank=False)
    weekStart = models.DateField(db_column='trafficDutyWeekStart', verbose_name='Traffic Duty Week Start', null=True, blank=False,db_index=True)
    weekEnd = models.DateField(db_column='trafficDutyWeekEnd', verbose_name='Traffic Duty Week End', null=True, blank=False,db_index=True)
    morning_shifts = models.IntegerField(db_column='morningShifts', verbose_name='Morning Shifts', null=True,blank=True, default=0, choices=TRAFFICDUTY_INT)
    afternoon_shifts = models.IntegerField(db_column='afternoonShifts', verbose_name='Afternoon Shifts', null=True,blank=True, default=0, choices=TRAFFICDUTY_INT)
    am_manager = models.BooleanField(db_column='am_manager', verbose_name='Supervisor',default=False)
    kindie = models.BooleanField(db_column='kindie', verbose_name='Kindie',default=False) #this is a test
    totalTrafficShifts =  models.DecimalField(db_column='totalTrafficShifts',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Total Traffic Shifts')
    volunteerHours = models.DecimalField(db_column='volunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Volunteer Hours')

    def __unicode__(self):
        return '%s -- %s through %s' %(self.volunteerId.name,self.weekStart,self.weekEnd)

    class Meta:
        verbose_name_plural='Traffic Duty'
        db_table = 'traffic_Duty'
        ordering = ['weekStart']

    def save(self, *args, **kwargs):
        #calcualte total volunteer hours
        if self.am_manager ==True:
            am_hours = float(self.morning_shifts ) *1.5
        else:
            am_hours = self.morning_shifts

        #caclulate kindie traffic shifts
        if self.kindie==True:
            self.totalTrafficShifts = float(self.morning_shifts * .5) + float(self.afternoon_shifts * .5)
            am_hours = float(self.morning_shifts) * .5
            pm_hours = float(self.afternoon_shifts) * .5
        else:
            #assign two hours to every afternoon shift
            pm_hours = self.afternoon_shifts*2
            #sum shifts and add to total traffic shifts
            self.totalTrafficShifts = float(self.morning_shifts) + float(self.afternoon_shifts)
        self.volunteerHours = float(am_hours)+float(pm_hours)



        #manage information in the family Aggregate table
        p, created = FamilyAggHours.objects.get_or_create(family = self.linkedFamily, schoolYear = self.schoolYear)
        if self.pk: #if this is an existing traffic duty record meaning we're updating an existing entry
            origRecord = Traffic_Duty.objects.get(pk=self.pk) #get Original record
            #back out all data from the original record. This should give us a clean slate to add back the updated data
            p.trafficDutyCount = float(p.trafficDutyCount) - float(origRecord.totalTrafficShifts)
            p.totalVolHours = p.totalVolHours - origRecord.volunteerHours
            #add back all new updated data
            p.trafficDutyCount = float(p.trafficDutyCount) + float(self.totalTrafficShifts)
            p.totalVolHours = float(p.totalVolHours) + float(self.volunteerHours)
        else: #if trafficDuty doesnt exist - this is a new entry
            p.trafficDutyCount = p.trafficDutyCount+self.totalTrafficShifts #increment
            p.totalVolHours = float(p.totalVolHours) + float(self.volunteerHours)
        p.save()
        super(Traffic_Duty,self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        p = FamilyAggHours.objects.get(family = self.linkedFamily, schoolYear = self.schoolYear)
        p.totalVolHours = p.totalVolHours - self.volunteerHours
        p.trafficDutyCount = p.trafficDutyCount - self.totalTrafficShifts
        p.save()
        super(Traffic_Duty, self).delete(*args, **kwargs)

class FamilyAggHours(TimeStampedModel):
    familySumId = models.AutoField(primary_key=True,db_column='FamilySumId',verbose_name='Family Sum ID')
    family = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name="Family",null=True,blank=False, related_name='familyAgg')
    schoolYear = models.ForeignKey(SchoolYear,db_column='schoolYear',null=True,blank=False, verbose_name='School Year')
    totalVolHours = models.DecimalField(db_column='totalVolunteerHours',max_digits=8, decimal_places=3,null=True, blank=True,verbose_name='Total Volunteer Hours', default=0)
    trafficDutyCount = models.IntegerField(db_column='trafficDutyCount',verbose_name='Traffic Duty Count',null=True, blank=True, default=0)

    def currentYear(self):
        curYear = self.objects.filter(schoolYear = SchoolYear.objects.get(currentYear=1))
        return curYear

    def __unicode__(self):
        return '%s - %s' %(self.family,self.schoolYear)

    def create_familyAgg_on_familyProfile_creation(sender, instance, created, **kwargs):
        if created:
            FamilyAggHours.objects.get_or_create(family = instance, schoolYear = SchoolYear.objects.get(currentYear = 1))
    post_save.connect(create_familyAgg_on_familyProfile_creation, sender=FamilyProfile)

    class Meta:
        verbose_name_plural='Family Sums'
        db_table = 'familyAggregate'
        ordering = ['family']
