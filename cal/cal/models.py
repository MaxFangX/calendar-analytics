from apiclient.discovery import build
from cal.constants import GOOGLE_CALENDAR_COLORS
from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import CredentialsField, FlowField
from oauth2client.client import AccessTokenRefreshError

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
    calendar_id = models.CharField(max_length=250)


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

    user = models.OneToOneField(User, primary_key=True, related_name='googlecredentials')
    credential = CredentialsField()
    next_sync_token = models.CharField(max_length=100, null=True, blank=True)

    def get_service(self):
        http_auth = self.credential.authorize(httplib2.Http())
        try:
            return build('calendar', 'v3', http=http_auth)
        except AccessTokenRefreshError:
            return None
        return None

    def import_calendars(self, only_primary=True):
        """
        Hits the CalendarList.list() endpoint and updates database with any calendars found.
        only_primary specifies if only the primary calendar is saved to the database.
        """
        
        service = self.get_service()
        result = service.calendarList().list().execute()

        # Example:
        # {
        #   "kind": "calendar#calendarList",
        #   "etag": etag,
        #   "nextPageToken": string,
        #   "nextSyncToken": string,
        #   "items": [
        #     {u'accessRole': u'owner',
        #      u'backgroundColor': u'#9fc6e7',
        #      u'colorId': u'15',
        #      u'defaultReminders': [{u'method': u'popup', u'minutes': 10}],
        #      u'etag': u'"1446592681590000"',
        #      u'foregroundColor': u'#000000',
        #      u'id': string,
        #      u'kind': u'calendar#calendarListEntry',
        #      u'notificationSettings': {u'notifications': [{u'method': u'email',
        #         u'type': u'eventCreation'},
        #        {u'method': u'email', u'type': u'eventChange'},
        #        {u'method': u'email', u'type': u'eventCancellation'},
        #        {u'method': u'email', u'type': u'eventResponse'}]},
        #      u'primary': True,
        #      u'selected': True,
        #      u'summary': u'maxfangx@gmail.com',
        #      u'timeZone': u'America/Los_Angeles'}
        #   ]
        # }

        assert 'items' in result and 'nextSyncToken' in result, "import_calendars failed"

        self.next_sync_token = result['nextSyncToken']

        for item in result['items']:
            if item.get('primary', False):
                # This is the primary calendar, save it as such
                gcal, _ = GCalendar.objects.get_or_create(user=self.user, calendar_id=item['id'])
                profile, _ = Profile.get_or_create(self.user)
                profile.main_calendar = gcal
                profile.save()
            elif not only_primary:
                gcal, _ = GCalendar.objects.get_or_create(user=self.user, calendar_id=item['id'])
        
        self.save()
