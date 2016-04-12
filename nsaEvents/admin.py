from django.contrib import admin
from .models import *
from nsaSchool.models import SchoolYear


# Register your models here.

class NsaEventsAdmin(admin.ModelAdmin):
    model = NsaEvents
    search_fields = ('eventName',)
    filter_horizontal = ('daysOfWeek',)
    list_display = ('eventName','eventLeader','eventDetailsDisplay','autoApprove')


admin.site.register(NsaEvents,NsaEventsAdmin)
admin.site.register(EventTasks)
#admin.site.register(DaysOfWeek)
