from django.contrib.auth.models import User
from django.db import models
from cal.constants import GOOGLE_CALENDAR_COLORS

EVENT_COLORS = GOOGLE_CALENDAR_COLORS['event'].keys()

class Profile(models.Model):

    user = models.OneToOneField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class UserCategory(models.Model):

    user = models.ForeignKey(User)
    color = models.CharField(max_length=100)
    label = models.CharField(max_length=100)


class GCalendar(models.Model):

    user = models.ForeignKey(User)


class Event(models.Model):

    name = models.CharField(max_length=1000)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GEvent(Event):

    calendar = models.ForeignKey(GCalendar)
    # TODO: Add choices for color
    color = models.CharField(max_length=10, choices=EVENT_COLORS)
    note = models.TextField(max_length=20000)


class Statistic(models.Model):

    user = models.ForeignKey(User)
    name = models.CharField(max_length=500)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
