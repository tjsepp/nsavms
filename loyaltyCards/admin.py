from django.contrib import admin
from loyaltyCards.models import *
# Register your models here.

class LoyaltyCardAdmin(admin.ModelAdmin):
    model = LoyaltyCardNumbers
    list_display = ('relatedFamily','loyaltyCardNumber','alternateId')
    search_fields = ('relatedFamily__familyName','loyaltyCardNumber','alternateId')

admin.site.register(LoyaltyCardNumbers,LoyaltyCardAdmin)