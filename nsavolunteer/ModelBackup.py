"""
class StudentToFamily(TimeStampedModel):
    stuToFamId = models.AutoField(primary_key=True,db_column='studentToFamilyId',verbose_name='StudentToFamilyId')
    family = models.ForeignKey(FamilyProfile, db_column='family', verbose_name='Family', null=True, blank=True)
    student = models.ForeignKey(Student, db_column='student', verbose_name='Student',null=True, blank=True)

    def __unicode__(self):
        return '%s - %s' %(self.student, self.family)

    class Meta:
        verbose_name_plural = 'Student To Family'
        db_table = 'studentToFamily'
        ordering = ['student']



class FamilyProfile(OrganizationBase):
    '''
    This creates a family/organization that allows for multiple users to be added. This will be the main unit used to
    roll up all data to a family level.
    '''
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
    '''
    model that relates the user to the family/group
    '''
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

"""

