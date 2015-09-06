from cal.models import GCalendar, Profile
from django.contrib import admin


class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)


class GCalendarAdmin(admin.ModelAdmin):
    pass

admin.site.register(GCalendar, GCalendarAdmin)
