from django.test import TestCase
from .models import FamilyProfile
# Create your tests here

class BasicFamilyProfileTest(TestCase):
    def test_fields(self):
        family = FamilyProfile()
        family.name = 'Smith Family'
        family.streetAddress = '1234 S.Clinton Ct'
        family.city ='Parker'
        family.zip = '80231'
        family.homePhone = '303-333-3333'
        family.specialInfo = 'This is a special message'
        family.specialInfo = '4/5/2020'
        family.active = True
        family.save()

        record = FamilyProfile.objects.get(pk=1)
        self.assertEqual(record,family)



'''
class FamilyProfile(OrganizationBase):
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
'''