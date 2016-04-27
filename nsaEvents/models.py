from django.db import models
from simple_history.models import HistoricalRecords
from authtools.models import User
from django.conf import settings



class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DaysOfWeek(models.Model):
    dayId = models.AutoField(primary_key=True,db_column='dayId',verbose_name='Week Day ID')
    dayName = models.CharField(max_length=25,db_column='dayName',verbose_name='Day',null=True,blank=False)
    dayAbbr = models.CharField(max_length=25,db_column='dayAbbr',verbose_name='Abbreviation',null=True,blank=False)

    def __unicode__(self):
        return self.dayName

    class Meta:
        verbose_name_plural = 'Days'
        db_table = 'nsaDaysofWeek'
        ordering = ['dayId']


class NsaEvents(TimeStampedModel):
    eventId= models.AutoField(primary_key=True,db_column='eventId',verbose_name='Event ID')
    eventName = models.CharField(max_length=100, db_column='eventName',verbose_name='Event Name', null=True,blank=False)
    eventDate = models.DateField(db_column='eventDate',verbose_name='Event Date',null=True,blank=True)
    eventLeader =models.ForeignKey(settings.AUTH_USER_MODEL,db_column='eventLeader',related_name='eventLeader')
    location = models.CharField(max_length=100, db_column='location',verbose_name='Location', null=True,blank=True)
    autoApprove = models.BooleanField(verbose_name='Auto Approve',db_column='autoApporve',default=True,blank=False)
    description = models.TextField(verbose_name='Event Description', db_column='eventDescription', null=True, blank=False)
    internalComments= models.TextField(verbose_name='Internal Comments', db_column='internamComments', null=True, blank=True)
    recurring = models.BooleanField(db_column='recurringEvent',verbose_name='recurring Event', default=False)
    daysOfWeek = models.ManyToManyField(DaysOfWeek,verbose_name='Days of the Week',blank =True)
    allowView = models.BooleanField(db_column='allowViewFlag',verbose_name='Allow Volunteers to view event', default=True)
    history = HistoricalRecords()

    def getDaysOfWeek(self):
        days = self.daysOfWeek.all()
        return 'Every %s'%(','.join([dd.dayAbbr for dd in days]))

    def eventDetailsDisplay(self):
        if self.recurring == True:
            return self.getDaysOfWeek()
        else:
            return self.eventDate

    def __unicode__(self):
        return self.eventName

    class Meta:
        verbose_name_plural = 'NSA Events'
        db_table = 'nsaEvents'
        ordering = ['eventName']


class EventTasks(TimeStampedModel):
    taskid =  models.AutoField(primary_key=True,db_column='taskId',verbose_name='Task ID')
    taskName =models.CharField(max_length=100, db_column='taskName',verbose_name='Task Name', null=True,blank=False)
    relatedEvent =models.ForeignKey(NsaEvents,db_column='linkedEvent',related_name='linkedEvent')
    approved = models.BooleanField(db_column='recurringEvent',verbose_name='recurring Event', default=False)

    def __unicode__(self):
        return self.taskName

    class Meta:
        verbose_name_plural = 'NSA Event Tasks'
        db_table = 'nsaEventtasks'
        ordering = ['taskName']
