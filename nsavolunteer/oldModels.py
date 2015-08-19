"""
class VolunteerProfile(TimeStampedModel):
    '''
    This class should be viewed as the account level profile. There should be a single profile per family.
    This will be the 'base' model that all other models will link to.
    '''
    volunteerProfileId =models.AutoField(primary_key=True,db_column='volunteerProfileId',verbose_name='Volunteer Profile Id')
    linkedUserAccount = models.OneToOneField(settings.AUTH_USER_MODEL)
    #streetAddress = models.CharField(db_column='streetAddress', max_length=200, null=True,blank=True,verbose_name='Street Address')
    #city = models.CharField(db_column='city', max_length=50, null=True,blank=True,verbose_name='city')
    #zip = models.CharField(db_column='zip', max_length=15, null=True,blank=True,verbose_name='zip')
    #homePhone = models.CharField(max_length=15,db_column='homePhone',verbose_name='Home Phone', null=True, blank=True, default=None)
    #specialInfo = models.TextField(verbose_name='Volunteer Note', db_column='VolunteerNote', null=True, blank=True)
    #doNotEmail = models.BooleanField(verbose_name='Do Not Email',db_column='emailOptOut',default=False)
    #inactiveDate = models.DateField(verbose_name='Inactive Date',db_column='inactiveDate',null=True,blank=True)
    #active =  models.BooleanField(verbose_name='active',db_column='active',default=True)
    #interest = models.ManyToManyField('nsavolunteer.VolunteerInterests',db_table ='profileToInterest',verbose_name='Volunteer Interests', null=True, blank =True, related_name='profile_interest')
    #volunteers = models.ManyToManyField('nsavolunteer.Volunteers',db_table ='profileToVolunteers',verbose_name='Volunteer', null=True, blank =True, related_name='profileToVol')
    history = HistoricalRecords()

    def __unicode__(self):
        return self.linkedUserAccount.name

    class Meta:
        verbose_name_plural='Volunteer Profile'
        db_table = 'volunteerProfile'
        ordering = ['volunteerProfileId']
"""

"""
class Volunteers(TimeStampedModel):
    volunteerId = models.AutoField(primary_key=True,db_column='volunteerId',verbose_name='Volunteer Id')
    volunteerType = models.ForeignKey('VolunteerType',null=True,blank=True,db_column='volunteerType',verbose_name='Volunteer Type')
    firstName = models.CharField(db_column='firstName', max_length=100, null=True,blank=True,verbose_name='First Name')
    lastName = models.CharField(db_column='lastName', max_length=100, null=True,blank=True,verbose_name='Last Name')
    email = models.EmailField(db_column='email',verbose_name='Email',null=True,blank=True, unique=True)
    cellPhone =models.CharField(max_length=15,db_column='cellPhone',verbose_name='cell Phone', null=True, blank=True, default=None)
    primaryContact = models.NullBooleanField(verbose_name='Primary Contact',db_column='primary',null=True,blank=True,default=None)
    relatedProfile = models.ForeignKey('VolunteerProfile',db_column='relatedProfile',verbose_name='Related Profile',blank=False,null=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return '%s %s' %(self.firstName,self.lastName)

    def fullName(self):
        return '%s %s' %(self.firstName,self.lastName)
    fullName.short_description = 'Full Name'

    class Meta:
        verbose_name_plural='Volunteers'
        db_table = 'volunteers'
        ordering = ['lastName']

"""