from apiclient.discovery import build
from cal.constants import GOOGLE_CALENDAR_COLORS
from cal.helpers import EventCollection, TimeNode, TimeNodeChain
from datetime import date, datetime, timedelta
from dateutil.rrule import rrulestr
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from jsonfield import JSONField
from oauth2client.django_orm import CredentialsField, FlowField
from oauth2client.client import AccessTokenRefreshError

import ast
import httplib2
import sys


class Profile(models.Model):

    user = models.OneToOneField(User)
    google_id = models.CharField(null=True, max_length=25)
    picture_url = models.URLField(null=True, blank=True)
    locale = models.CharField(max_length=10, default='en')
    main_calendar = models.ForeignKey("GCalendar", null=True)
    authed = models.BooleanField(default=False, help_text="If the user's oauth credentials are currently valid")
    analysis_start = models.DateTimeField(null=True, blank=True, help_text="When the analysis of the user's calendar will start")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return "{}'s profile".format(self.user)

    def clear_credentials(self):
        qs = GoogleCredentials.objects.filter(user=self.user)
        if qs:
            qs.last().delete()
        self.authed = False
        self.save()


class ColorCategory(models.Model, EventCollection):

    user = models.ForeignKey(User, related_name='colorcategories')
    color = models.CharField(max_length=100, help_text="str of the number of the event color in constants.py")
    label = models.CharField(max_length=100)
    # Consider adding a ForeignKey(null=True) to this model to allow for
    # categorizing on multiple calendars

    def __str__(self):
        return "{} by {}".format(self.label, self.user.username)

    def get_events(self, calendar=None):
        if not calendar:
            calendar = self.user.profile.main_calendar

        qs = GEvent.objects.filter(calendar__user=self.user, calendar=calendar, color_index=self.color)
        return set(qs)

    def get_last_week(self, calendar=None):
        """
        Returns the last week's worth of GEvents in a calendar
        """
        if not calendar:
            calendar = self.user.profile.main_calendar

        qs = GEvent.objects.filter(calendar__user=self.user, calendar=calendar, color_index=self.color)
        now = date.today()
        one_week_ago = now - timedelta(days=7)
        qs = qs.filter(start__range=(one_week_ago, now), end__range=(one_week_ago, now))
        qs = qs.order_by('updated')
        return qs

    def get_last_month(self, calendar=None):
        if not calendar:
            calendar = self.user.profile.main_calendar

        qs = GEvent.objects.filter(calendar__user=self.user, calendar=calendar, color_index=self.color)
        now = date.today()
        one_month_ago = now - timedelta(days=28)  # 28 days to maintain consistency between weeks
        qs = qs.filter(start__range=(one_month_ago, now), end__range=(one_month_ago, now))
        qs = qs.order_by('updated')
        return qs


class TagGroup(models.Model):

    user = models.ForeignKey(User, related_name='taggroups')
    label = models.CharField(max_length=100, help_text="The name of this tag family")

class Tag(models.Model, EventCollection):

    user = models.ForeignKey(User, related_name='tags')
    label = models.CharField(max_length=100, help_text="The name of this tag")
    keywords = models.CharField(max_length=100, help_text="Comma-separated list of strings to search for")
    group = models.ForeignKey(TagGroup, null=True, default=None, related_name='tags')

    def __str__(self):
        return "<Tag '{}'>".format(self.label, self.keywords)

    def save(self, *args, **kwargs):
        # Remove beginning and ending spaces
        self.keywords = ",".join([k.strip() for k in self.keywords.split(',')])

        return super(Tag, self).save(*args, **kwargs)

    def get_events(self, calendar=None):
        return set(self.query(calendar))

    def query(self, calendar=None):
        """
        Returns a QuerySet of events matching this Tag
        """
        if calendar:
            # Check that this calendar belongs to the User
            if calendar.user != self.user:
                # TODO replace this with appropriate exception
                return []
        else:
            # Try to use the main calendar
            calendar = self.user.profile.main_calendar
            if not calendar:
                # TODO replace this with appropriate exception
                return []

        keywords = self.keywords.split(',')
        if not keywords:
            return []

        querysets = set()
        for kw in keywords:
            # TODO extend this be able to search in note as well
            qs = GEvent.objects.filter(calendar=calendar, name__icontains=kw)
            querysets.add(qs)

        # Union over the querysets
        events_qs = reduce(lambda qs1, qs2: qs1 | qs2, querysets)

        return events_qs.order_by('start')


class GCalendar(models.Model):
    
    """
    Represents a Google Calendar. The GEvents associated with this are designed to maintain
    the state of the User's Google Calendar.
    """

    user = models.ForeignKey(User, related_name='gcalendars')
    calendar_id = models.CharField(max_length=250)
    meta = JSONField(default="{}", blank=True)

    def __str__(self):
        return "{}'s calendar {}".format(self.user, self.calendar_id)

    def sync(self, full_sync=False):
        result = None
        creds = self.user.googlecredentials
        service = creds.get_service()

        def update_event(event):
            """
            Helper function to take care of duplicate code
            """
            if event.get('status', 'confirmed') in set(['confirmed', 'tentative']):
                # Create or update the event
                try:
                    g = GEvent.objects.get(id_event=event['id'])
                except GEvent.DoesNotExist:
                    g = GEvent()
                g.name = event.get('summary', '')
                if event['start'].get('dateTime'):
                    # This is a date time
                    g.start = parse_datetime(event['start']['dateTime'])
                    g.end = parse_datetime(event['end']['dateTime'])
                else:
                    # This is a date, convert it to a datetime starting/ending at midnight
                    g.start = datetime.combine(parse_date(event['start']['date']), datetime.min.time())
                    g.end = g.start + timedelta(days=1)
                    g.all_day_event = True
                g.location = event.get('location', '')
                if event.get('created', None):
                    g.created = parse_datetime(event['created'])
                    g.updated = parse_datetime(event['updated'])

                g.calendar = self
                g.id_event = event['id']
                g.i_cal_uid = event['iCalUID']
                g.color_index = event.get('colorId', '')
                g.description = event.get('description', '')
                g.status = event.get('status', 'confirmed')
                g.transparency = event.get('transparency', 'opaque')
                g.all_day_event = True if event['start'].get('date', None) else False
                if not g.all_day_event:
                    # Some events don't have timezones
                    g.timezone = event['start'].get('timeZone')
                g.end_time_unspecified = event.get('endTimeUnspecified', False)
                g.recurrence = str(event.get('recurrence', ''))
                g.recurring_event_id = event.get('recurringEventId', '')
                g.save()

            else:  # Status is cancelled, delete the event
                try:
                    query = GEvent.objects.get(calendar=self, id_event=event['id'])
                    query.delete()
                except GEvent.DoesNotExist:
                    pass

        next_page_token = None

        if full_sync:
            # Full sync - initial request without sync token or page token
            result = service.events().list(calendarId=self.calendar_id).execute()
            old_events = GEvent.objects.filter(calendar=self)
            for event in old_events:
                event.delete()
        else:
            # Incremental sync, initial request needs syncToken
            try:
                result = service.events().list(calendarId=self.calendar_id, syncToken=creds.next_sync_token).execute()
            except Exception as e:
                t, v, tb = sys.exc_info()
                if hasattr(e, 'resp') and e.resp.status == 410:
                    # Sync token is no longer valid, perform full sync
                    result = service.events().list(calendarId=self.calendar_id).execute()
                else:
                    raise t, v, tb

        # Run the first iteration, for the first request
        for item in result['items']:
            update_event(item)

        # Paginate through the rest, if applicable
        while True:
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                # We've reached the last page. Store the sync token.
                creds.next_sync_token = result['nextSyncToken']
                creds.save()
                break

            result = service.events().list(calendarId=self.calendar_id, pageToken=next_page_token).execute()

            # Assume at this point it's a correctly formatted event
            for item in result['items']:
                update_event(item)

        print "Successfully synced calendar."

    def update_recurring(self, end=None):
        """
        Fill in recurring events up to the end time
        """
        # TODO consider adding a field to GCalendar that models how far forward
        # recurring events has been updated
        # TODO in incremental sync, if future exceptions have been made, sync up to at least that point
        # TODO sanity checks - don't fill for more than a year in advance
        if not end:
            # By default, fill in two months past the present time
            end = datetime.now() + timedelta(days=60)
        unique_events = GEvent.objects.filter(calendar=self).exclude(recurrence__exact='')
        for gevent in unique_events:
            gevent.fill_recurrences(end=end)


    def find_gaps(self, start=None, end=None):
        qs = GEvent.objects.filter(calendar=self)
        if start:
            qs = qs.filter(start__gte=start)
        if end:
            qs = qs.filter(end__lte=end)
        qs.order_by('start')

        return qs

    def time_log(self):
        """
        Forms a TimeNodeChain based off events in this Calendar
        """
        return TimeNodeChain(GEvent.objects.filter(calendar=self).order_by('updated'))

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

class Event(models.Model, TimeNode):

    name = models.CharField(max_length=150, default="(No title)", blank=True)
    start = models.DateTimeField(help_text="When the event started. 12AM for all day events")
    end = models.DateTimeField(help_text="When the event ended. 12AM the next day for all day events")
    location = models.CharField(max_length=500, blank=True, help_text="Geographic location as free form text")
    created = models.DateTimeField(help_text="When the event was created, on Google")
    updated = models.DateTimeField(help_text="When the event was last updated, on Google")

    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):

        TimeNode.__init__(self, start=kwargs.get('start'), end=kwargs.get('end'), id=kwargs.get('id'))

        super(Event, self).__init__(*args, **kwargs)


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
    color_index = models.CharField(max_length=10, blank=True, choices=EVENT_COLORS)
    description = models.TextField(max_length=20000, blank=True)
    status = models.CharField(max_length=50, default='confirmed', blank=True, choices=STATUS_CHOICES)
    transparency = models.CharField(max_length=50, default='opaque', blank=True, choices=TRANSPARENCY_CHOICES, help_text="Whether the event blocks time on the calendar.")

    all_day_event = models.BooleanField(default=False, blank=True)
    timezone = models.CharField(max_length=200, null=True, blank=True, help_text="IANA Time Zone Database Name")
    end_time_unspecified = models.BooleanField(default=False, help_text="If an end time is actually unspecified, since an end time is always specified for compatibility reasons")
    # Use ast.literal_eval(event.recurrence) to retrieve the list
    recurrence = models.CharField(max_length=1000, blank=True, help_text="string representation of list of RRULE, EXRULE, RDATE and EXDATE lines for a recurring event, as specified in RFC5545")
    recurring_event_id = models.CharField(max_length=1024, blank=True, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")

    # TODO handle all_day_event not being counted in time
    # TODO handle transparency being counted in time

    def __str__(self):
        return "{} | {}".format(self.id, self.name)

    @property
    def color(self):
        color = GOOGLE_CALENDAR_COLORS['event'].get(self.color_index)
        if color:
            return color
        else:
            # This handles when data isn't consistent for some reason.
            # TODO migration for blank=False in color_index attribute, then remove this
            print "Warning: GEvent '{}' with id {} has an incorrect color_index value of '{}'".format(self.name, self.id, self.color_index)
            return GOOGLE_CALENDAR_COLORS['event']['1']

    def save(self, *args, **kwargs):
        if self.name is None:
            self.name = ""
        self.name = self.name[:150]

        if self.description is None:
            self.description = ""
        self.description = self.description[:20000]

        # TODO fix naive timezone bug
        # if timezone.is_naive(self.start):

        super(GEvent, self).save(*args, **kwargs)

    def fill_recurrences(self, end=None):

        if not self.recurrence:
            return

        if end:
            assert self.start <= end, "Can't fill in recurrences for a negative time window"
        else:
            # By default, fill in two months past the present time
            end = datetime.now() + timedelta(days=60)

        # For some reason, times have to be timezone-naive for rrule parsing
        start = self.start.astimezone(timezone.utc).replace(tzinfo=None)
        end = end.astimezone(timezone.utc).replace(tzinfo=None)

        # self.recurrence looks like this:
        u"[u'RRULE:FREQ=WEEKLY;WKST=MO;UNTIL=20160502T155959Z;BYDAY=MO,WE']"
        # Convert to string
        rules = ast.literal_eval(self.recurrence)
        duration = self.end - self.start
        for rule_string in rules:
            rule = rrulestr(rule_string)
            recurrences = rule.between(after=start, before=end)
            assert len(recurrences) < 1000, "Let's not pollute our database"
            for instance_of_start_time in recurrences:
                # Make times timezone aware again for saving into the database
                tz_aware_start_time = timezone.make_aware(instance_of_start_time, timezone.get_default_timezone())
                GRecurrence.objects.get_or_create(calendar=self.calendar,
                                                  start=instance_of_start_time,
                                                  end=instance_of_start_time + duration)

        # TODO check for offset events and delete them. probably just delete all recurrences once there has been a change

    def conflicts_with(self, gevent):
        """
        Takes in another GEvent and returns True if the two events conflict, false otherwise.
        """
        # TODO incorporate this
        return False if self.end <= gevent.start or self.start >= gevent.end else True


class GRecurrence(models.Model):

    calendar = models.ForeignKey(GCalendar, related_name='recurrences')
    start = models.DateTimeField()
    end = models.DateTimeField()
    recurring_event_id = models.CharField(max_length=1024, blank=True, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")


class Statistic(models.Model):

    user = models.ForeignKey(User, related_name='statistics')
    name = models.CharField(max_length=100, help_text="The name of the statistic ")
    start_time = models.DateTimeField(null=True, help_text="The starting point for this statistic")
    end_time = models.DateTimeField(null=True, help_text="The ending point for this statistic")

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
                break
            except Exception:
                pass

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
