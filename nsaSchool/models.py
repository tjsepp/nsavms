from django.db import models
from simple_history.models import HistoricalRecords
from tinymce import models as tinymce_models



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
        ordering = ['-dateCreated']



class GradeLevel(models.Model):
    gradeId = models.AutoField(primary_key=True,db_column='gradeId',verbose_name='Grade ID')
    gradeName = models.CharField(max_length=25, db_column='gradeName', null=True, blank=False,verbose_name='Grade Name')
    gradeOrder = models.IntegerField(db_column='gradeOrder',unique=True,null=True,blank=True, verbose_name='Grade Order')


    def __unicode__(self):
        return self.gradeName

    class Meta:
        verbose_name_plural='Grade Level'
        db_table = 'gradeLevel'
        ordering = ['gradeOrder']



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



class Teachers(TimeStampedModel):
    teacherId = models.AutoField(primary_key=True,db_column='teacherId',verbose_name='Teacher ID')
    firstName = models.CharField(max_length=30, db_column='firstName',null=True, blank=True,verbose_name='First Name')
    lastName = models.CharField(max_length=30, db_column='lastName',null=True, blank=True,verbose_name='Last Name')
    gradeLevel = models.ForeignKey('GradeLevel',db_column='gradeLevel',null=True,blank=True, verbose_name='Grade Level')
    activeStatus = models.BooleanField(verbose_name='Active Status',default=True,db_column='activeStatus')

    def __unicode__(self):
        return '%s %s' %(self.firstName, self.lastName)

    class Meta:
        verbose_name_plural = 'Teachers'
        db_table='teachers'
        ordering =['lastName']
