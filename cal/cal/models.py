from apiclient.discovery import build
from cal.constants import GOOGLE_CALENDAR_COLORS
from django.contrib.auth.models import User
from django.db import models
from django.utils.dateparse import parse_datetime
from jsonfield import JSONField
from oauth2client.django_orm import CredentialsField, FlowField
from oauth2client.client import AccessTokenRefreshError

import httplib2

# TODO make this more readable

class Profile(models.Model):

    user = models.OneToOneField(User)
    google_id = models.CharField(null=True, max_length=25)
    picture_url = models.URLField(null=True, blank=True)
    locale = models.CharField(max_length=10, default='en')
    main_calendar = models.ForeignKey("GCalendar", null=True)
    authed = models.BooleanField(default=False, help_text="If the user's oauth credentials are currently valid")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # TODO add a field for when calendar analysis will start

    @classmethod
    def get_or_create(cls, user):
        created = False
        try:
            profile = cls.objects.get(user=user)
        except cls.DoesNotExist:
            # Create a profile
            created = True
            profile = cls(user=user)
            profile.save()
        return profile, created


class UserCategory(models.Model):

    user = models.ForeignKey(User, related_name='usercategories')
    color = models.CharField(max_length=100)
    label = models.CharField(max_length=100)


class GCalendar(models.Model):
    
    """
    Represents a Google Calendar. The GEvents associated with this are designed to maintain
    the state of the User's Google Calendar.
    """

    user = models.ForeignKey(User, related_name='gcalendars')
    calendar_id = models.CharField(max_length=250)
    meta = JSONField(default="{}", blank=True)

    def sync(self, full_sync=False):
        if full_sync:
            result = None
            try:
                service = self.user.googlecredentials.get_service()
                result = service.events().list(calendarId=self.calendar_id).execute()
            except Exception as e:
                raise ("Could not sync. Error: {}".format(e))

            # Assume at this point it's a correctly formatted event
            for event in result['items']:
                if event.get('status', 'confirmed') in ['confirmed', 'tentative']:
                    # Create or update the event
                    g, _ = GEvent.objects.get_or_create(id_event=event['id'])
                    g.name = event.get('summary', '')
                    if event['start'].get('dateTime'):
                        # This is a date time
                        g.start = parse_datetime(event['start']['dateTime'])
                        g.end = parse_datetime(event['end']['dateTime'])
                    else:
                        # TODO This is a date, convert it to a datetime
                        pass
                    g.location = event.get('location', '')
                    if event.get('created', None):
                        g.created = parse_datetime(event['created'])
                        g.updated = parse_datetime(event['updated'])

                    g.calendar = self
                    g.id_event = event['id']
                    g.i_cal_uid = event['iCalUID']
                    g.color = event.get('colorId', '')
                    g.description = event.get('description', '')
                    g.status = event.get('status', 'confirmed')
                    g.transparency = event.get('transparency', 'opaque')
                    g.all_day_event = True if event['start'].get('date', None) else False
                    g.end_timezone = event['start']['timeZone']
                    g.end_time_unspecified = event.get('endTimeUnspecified', False)
                    g.recurring_event_id = event.get('recurringEventId', '')
                    g.save()

                else:
                    # TODO delete the event
                    pass

        raise NotImplementedError()

    def update_meta(self):
        service = self.user.googlecredentials.get_service()
        try:
            result = service.calendars().get(calendarId=self.calendar_id).execute()
        except Exception as e:
            raise Exception("Could not update meta for GCalendar {}. Error: {}".format(self.calendar_id, e))
        # `result` looks like this:
        # {
        #     u'etag': u'[redacted]',
        #     u'id': u'maxfangx@gmail.com',
        #     u'kind': u'calendar#calendar',
        #     u'summary': u'maxfangx@gmail.com',
        #     u'timeZone': u'Asia/Shanghai'
        # }

        # Prune duplicate values
        if result and 'id' in result:
            result.pop('id')
        self.meta = result
        self.save()

class Event(models.Model):

    name = models.CharField(max_length=150, default="(No name)", blank=True)
    start = models.DateTimeField(help_text="When the event started. 12AM for all day events")
    end = models.DateTimeField(help_text="When the event ended. 12AM the next day for all day events")
    location = models.CharField(max_length=500, blank=True, help_text="Geographic location as free form text")
    created = models.DateTimeField(help_text="When the event was created, on Google")
    updated = models.DateTimeField(help_text="When the event was last updated, on Google")

    class Meta:
        abstract = True


class GEvent(Event):

    """
    Represents a Google event.

    Reference:
    https://developers.google.com/google-apps/calendar/v3/reference/events#resource-representations
    """

    EVENT_COLORS = [(k, GOOGLE_CALENDAR_COLORS['event'][k]['background']) for k in GOOGLE_CALENDAR_COLORS['event'].keys()]  # '1', '2', '3', etc

    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('tentative', 'Tentative'),
        ('cancelled', 'Cancelled'),
    )

    TRANSPARENCY_CHOICES = (
        ('opaque', "Opaque - The event blocks time on the calendar"),
        ('transparent', "Transparent - The event does not block time on the calendar"),
    )

    # TODO support attendees for analyzing spending time with other people

    calendar = models.ForeignKey(GCalendar, related_name='gevents')
    id_event = models.CharField(max_length=1024, help_text="Unique id per calendar")
    i_cal_uid = models.CharField(max_length=1024, help_text="Unique id across calendaring systems. Only 1 per recurring event")
    color = models.CharField(max_length=10, blank=True, choices=EVENT_COLORS)
    description = models.TextField(max_length=20000, blank=True)
    status = models.CharField(max_length=50, default='confirmed', blank=True, choices=STATUS_CHOICES)
    transparency = models.CharField(max_length=50, default='opaque', blank=True, choices=TRANSPARENCY_CHOICES, help_text="Whether the event blocks time on the calendar.")

    all_day_event = models.BooleanField(default=False, blank=True)
    end_timezone = models.CharField(max_length=200, blank=True, help_text="IANA Time Zone Database Name")
    end_time_unspecified = models.BooleanField(default=False, help_text="If an end time is actually unspecified, since an end time is always specified for compatibility reasons")
    recurring_event_id = models.CharField(max_length=1024, blank=True, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")

    # TODO handle all_day_event not being counted in time
    # TODO handle transparency being counted in time
    # TODO on save, handle description length
    # TODO on save, handle title length
    # TODO change default of title to google calendar default


class Statistic(models.Model):

    user = models.ForeignKey(User, related_name='statistics')
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    # TODO Include helpful help_text
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

        # Try up to 3 times
        for _ in range(3):
            try:
                return build('calendar', 'v3', http=http_auth)
            except AccessTokenRefreshError:
                # TODO add logging to see this exception
                profile = Profile.get_or_create(self.user)[0]
                profile.authed = False
                profile.save()

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
                gcal, gcal_created = GCalendar.objects.get_or_create(user=self.user, calendar_id=item['id'])
                if gcal_created:
                    gcal.update_meta()
                profile, _ = Profile.get_or_create(self.user)
                profile.main_calendar = gcal
                profile.save()
            elif not only_primary:
                gcal, gcal_created = GCalendar.objects.get_or_create(user=self.user, calendar_id=item['id'])
                if gcal_created:
                    gcal.update_meta()
        
        self.save()
