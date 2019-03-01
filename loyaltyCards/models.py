from django.db import models
from nsavolunteer.models import FamilyProfile

class TimeStampedModel(models.Model):
    '''
    An abstract base class that provides self-updating 'created' and 'modified' fields.
    '''
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LoyaltyCardNumbers(TimeStampedModel):
    loyaltyCardID = models.AutoField(primary_key=True, db_column='loyaltyCardId',verbose_name='Loyalty Card Id')
    relatedFamily = models.ForeignKey(FamilyProfile,db_column='relatedFamily',verbose_name='Family',null=False, blank=False)
    loyaltyCardNumber = models.CharField(db_column='loyaltyCardNumber', max_length=20, null=False, blank=False,verbose_name='Loyalty Card Number')
    alternateId = models.CharField(db_column='alternateId', max_length=10, null=True, blank=True,verbose_name='Alternate ID')

    def __unicode__(self):
        return self.relatedFamily.familyName

    class Meta:
        verbose_name_plural = 'Loyalty Card Numbers'
        db_table = 'loyaltyCardNumbers'
        ordering = ['dateCreated']
        unique_together = ("loyaltyCardNumber", "relatedFamily")
