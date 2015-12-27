from apiclient.discovery import build
from cal.constants import GOOGLE_CALENDAR_COLORS
from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import CredentialsField, FlowField

import httplib2

EVENT_COLORS = [(key, GOOGLE_CALENDAR_COLORS['event'][key]['background']) for key in GOOGLE_CALENDAR_COLORS['event']]

class Profile(models.Model):

    user = models.OneToOneField(User)
    google_id = models.CharField(null=True, max_length=25)

    picture_url = models.URLField(null=True, blank=True)
    locale = models.CharField(max_length=10, default='en')

    main_calendar = models.ForeignKey("GCalendar", null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create(cls, user):
        created = False
        try:
            profile = cls.objects.get(user=user)
        except cls.DoesNotExist:
            # Create a profile, but don't save it yet
            created = True
            profile = cls(user=user)
            profile.save()
        return profile, created


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
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def query(self):
        qs = GEvent.objects.filter(user=self.user, name=self.name)
        if self.start_time:
            qs.filter(start_time__gt=self.start_time)
        if self.end_time:
            qs.filter(end_time__gt=self.end_time)
        return qs


class GoogleFlow(models.Model):
    """
    Represents a Google oauth flow.
    See: https://developers.google.com/api-client-library/python/guide/django
    """

    id = models.OneToOneField(User, primary_key=True)
    flow = FlowField()


class GoogleCredentials(models.Model):
    """
    Represents Google oauth credentials.
    See: https://developers.google.com/api-client-library/python/guide/django
    """

    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()

    def get_service(self):
        http_auth = self.credential.authorize(httplib2.Http())
        return build('calendar', 'v3', http=http_auth)
