from django.contrib import admin
from .models import *


# Register your models here.

class NsaEventsAdmin(admin.ModelAdmin):
    model = NsaEvents
    search_fields = ('eventName',)
    filter_horizontal = ('daysOfWeek',)
    list_display = ('eventName','eventLeader','eventDetailsDisplay','autoApprove')
    #raw_id_fields = ('linkedUserAccount',)

admin.site.register(NsaEvents,NsaEventsAdmin)
#admin.site.register(DaysOfWeek)
