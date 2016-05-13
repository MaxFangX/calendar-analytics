from cal.models import GCalendar, Profile, GEvent
from django.contrib import admin


class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)


class GCalendarAdmin(admin.ModelAdmin):
    pass

admin.site.register(GCalendar, GCalendarAdmin)


class GEventAdmin(admin.ModelAdmin):
    fields = ('calendar', 'google_id', 'i_cal_uid', 'color', 'description', 'status', 'transparency', 'all_day_event', ('timezone', 'end_time_unspecified'), 'recurring_event_id')

admin.site.register(GEvent, GEventAdmin)
