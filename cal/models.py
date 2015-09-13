from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from oauth2client.client import OAuth2WebServerFlow


class Profile(models.Model):

    user = models.OneToOneField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class GCalendar(models.Model):

    user = models.ForeignKey(User)

    def authenticate(self):
        OAuth2WebServerFlow(client_id=settings.GOOGLE_CALENDAR_API_CLIENT_ID,
                                   client_secret=settings.GOOGLE_CALENDAR_API_CLIENT_SECRET,
                                   scope='https://www.googleapis.com/auth/calendar',
                                   redirect_uri=settings.BASE_URL + '/auth/google')

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
    color = models.CharField(max_length=100)
    note = models.TextField(max_length=20000)
