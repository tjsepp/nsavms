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


class NsaEvents(TimeStampedModel):
    eventName = models.CharField(max_length=100, db_column='eventName',verbose_name='Event Name', null=True,blank=False)
    eventDate = models.DateField(db_column='eventDate',verbose_name='Event Date',null=True,blank=True)
    eventLeader =models.ForeignKey(settings.AUTH_USER_MODEL,db_column='eventLeader',related_name='eventLeader')
    location = models.CharField(max_length=100, db_column='location',verbose_name='Location', null=True,blank=True)
    autoApprove = models.BooleanField(verbose_name='Auto Approve',db_column='autoApporve',default=True,blank=False)
    description = models.TextField(verbose_name='Event Description', db_column='eventDescription', null=True, blank=False)
    internalComments= models.TextField(verbose_name='Internal Comments', db_column='internamComments', null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'NSA Events'
        db_table = 'nsaEvents'
        ordering = ['eventName']

