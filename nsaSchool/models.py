from django.db import models
from simple_history.models import HistoricalRecords


class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class SchoolYear(TimeStampedModel):
    '''
    This model will give us the ability to define the school year. Over rode the save method
     to define the current year. If current year is selected, all others will be set to 0.
     '''
    yearId = models.AutoField(primary_key=True,db_column='yearId',verbose_name='School Year ID')
    schoolYear = models.CharField(db_column='schoolYear', max_length=100, null=False,blank=False,verbose_name='School Year')
    currentYear = models.BooleanField(db_column='currentYear',verbose_name='Current Year', default=False)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.schoolYear

    def save(self, *args, **kwargs):
        if self.currentYear:
            SchoolYear.objects.filter(
                currentYear=True).update(currentYear=False)
        super(SchoolYear, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural='School Year'
        db_table = 'schoolYear'
        ordering = ['schoolYear']