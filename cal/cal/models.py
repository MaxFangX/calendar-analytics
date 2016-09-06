from apiclient.discovery import build
from cal.constants import GOOGLE_CALENDAR_COLORS
from cal.helpers import EventCollection, TimeNode, TimeNodeChain, ensure_timezone_awareness
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from jsonfield import JSONField
from oauth2client.django_orm import CredentialsField, FlowField
from oauth2client.client import AccessTokenRefreshError

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

    def create_calendars(self, only_primary=True):
        if only_primary and self.main_calendar:
            return False
        self.user.googlecredentials.import_calendars(only_primary)
        return self.main_calendar

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

    def __str__(self):
        return "{} by {}".format(self.label, self.user.username)

    @property
    def hours(self):
        return self.total_time() / 3600

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

    @property
    def hours(self):
        return self.total_time() / 3600

    def save(self, *args, **kwargs):
        # Remove beginning and ending spaces
        self.keywords = ",".join([k.strip() for k in self.keywords.split(',')])

        return super(Tag, self).save(*args, **kwargs)

    def get_events(self):
        """
        Overrides EventCollection.get_events
        """
        return set(self.query())

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
    summary = models.CharField(max_length=250, help_text="Title of the calendar")
    meta = JSONField(default="{}", blank=True)

    def __str__(self):
        return "{}'s calendar {}".format(self.user, self.calendar_id)

    def api_event_to_gevent(self, event):
        if event.get('status', 'confirmed') in set(['confirmed', 'tentative']):
            # Create or update the event

            try:
                g = GEvent.objects.get(google_id=event['id'])
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
            g.google_id = event['id']
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
            print "Saved {} event".format(g.start)
            return g

        else:
            print "Deleting event {}".format(event['id'])
            # Status is cancelled, create a DeletedEvent

            # 'event' looks like this:
            # {
            #     u'status': u'cancelled',
            #     u'kind': u'calendar#event',
            #     u'originalStartTime': {u'dateTime': u'2014-10-23T11:00:00-07:00'},
            #     u'etag': u'"2827884681552000"',
            #     u'recurringEventId': u'bpbt1o1k55c4hnv9ig9uet69ns',
            #     u'id': u'bpbt1o1k55c4hnv9ig9uet69ns_20141023T180000Z'
            # }
            if event.get('originalStartTime'):
                if event['originalStartTime'].get('dateTime'):
                    # This is a date time
                    original_start_time = parse_datetime(event['originalStartTime']['dateTime'])
                else:
                    # This is a date, convert it to a datetime
                    original_start_time = datetime.combine(parse_date(event['originalStartTime']['date']), datetime.min.time())
            else:
                original_start_time = None

            DeletedEvent.objects.get_or_create(
                calendar=self,
                google_id=event['id'],
                original_start_time=original_start_time,
                recurring_event_id=event.get('recurringEventId', ''))

    def sync(self, full_sync=False):
        result = None
        creds = self.user.googlecredentials
        service = creds.get_service()

        default_list_args = {
                'calendarId': self.calendar_id,
                'singleEvents': True,
                'maxResults': 2500,
                }
        list_args_with_constraints = {
                # Only sync up to two months in the future
                'timeMax': ensure_timezone_awareness(datetime.now() + timedelta(days=60)).isoformat(),
                }
        list_args_with_constraints.update(default_list_args)

        next_page_token = None
        if full_sync:
            # Full sync - initial request without sync token or page token
            result = service.events().list(**list_args_with_constraints).execute()
            old_events = GEvent.objects.filter(calendar=self)
            for event in old_events:
                event.delete()
            # Delete the DeletedEvents and get a fresh copy from Google
            deleted_events = DeletedEvent.objects.filter(calendar=self)
            for event in deleted_events:
                event.delete()
        else:
            # Incremental sync, initial request needs syncToken
            try:
                # Google API doesn't accept constraints for the first request in incremental sync
                result = service.events().list(syncToken=creds.next_sync_token, **default_list_args).execute()
            except Exception as e:
                t, v, tb = sys.exc_info()
                if hasattr(e, 'resp') and e.resp.status == 410:
                    # Sync token is no longer valid, perform full sync
                    result = service.events().list(**list_args_with_constraints).execute()
                else:
                    raise t, v, tb

        # Run the first iteration, for the first request
        for item in result['items']:
            self.api_event_to_gevent(item)

        # Paginate through the rest, if applicable
        while True:
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                # We've reached the last page. Store the sync token.
                creds.next_sync_token = result['nextSyncToken']
                creds.save()
                break

            result = service.events().list(pageToken=next_page_token, **list_args_with_constraints).execute()

            # Assume at this point it's a correctly formatted event
            for item in result['items']:
                self.api_event_to_gevent(item)

        # Make this calendar consistent with existing DeletedEvents
        deleted_events = DeletedEvent.objects.filter(calendar=self)
        for d_event in deleted_events:
            d_event.apply()

        print "Successfully synced calendar."

        # Some additional sanity checks
        # Check for non-duplicate events with the same recurring_event_id
        start_times = {}
        for recurrence in GEvent.objects.filter(calendar=self).exclude(recurrence=''):
            if recurrence.start in start_times.get(recurrence.recurring_event_id, set()):
                print "Error: Multiple GEvents found with the same start and recurring_event_id"
                dupe_ids = [str(dupe.id) for dupe in GEvent.objects.filter(recurring_event_id=recurrence.recurring_event_id,
                                                                start=recurrence.start)]
                print "IDs are {} at time {}".format(", ".join(dupe_ids), recurrence.start)

            if not start_times.get(recurrence.recurring_event_id, None):
                start_times[recurrence.recurring_event_id] = set()
            start_times[recurrence.recurring_event_id].add(recurrence.start)

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

        self.summary = result.get('summary')
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

    EVENT_COLORS_KEYS = sorted(GOOGLE_CALENDAR_COLORS['event'].keys(), key=lambda x: int(x))
    EVENT_COLORS_TUPLES = [(k, GOOGLE_CALENDAR_COLORS['event'][k]['background']) for k in EVENT_COLORS_KEYS]

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
    google_id = models.CharField(max_length=1024, help_text="Unique id per calendar")
    i_cal_uid = models.CharField(max_length=1024, help_text="Unique id across calendaring systems. Only 1 per recurring event")
    color_index = models.CharField(max_length=10, blank=False, choices=EVENT_COLORS_TUPLES)
    description = models.TextField(max_length=20000, blank=True)
    status = models.CharField(max_length=50, default='confirmed', blank=True, choices=STATUS_CHOICES)
    transparency = models.CharField(max_length=50, default='opaque', blank=True, choices=TRANSPARENCY_CHOICES, help_text="Whether the event blocks time on the calendar.")

    all_day_event = models.BooleanField(default=False, blank=True)
    timezone = models.CharField(max_length=200, null=True, blank=True, help_text="IANA Time Zone Database Name")
    end_time_unspecified = models.BooleanField(default=False, help_text="If an end time is actually unspecified, since an end time is always specified for compatibility reasons")
    # Use ast.literal_eval(event.recurrence) to retrieve the list
    recurrence = models.CharField(max_length=1000, blank=True, help_text="string representation of list of RRULE, EXRULE, RDATE and EXDATE lines for a recurring event, as specified in RFC5545")
    recurring_event_id = models.CharField(max_length=1024, blank=True, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")
    # recurrences_filled_until = models.DateTimeField(null=True, help_text="How far in advance we have filled in recurrences")

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
            print "Warning: GEvent '{}' with id {} has an incorrect color_index value of '{}'".format(self.name, self.id, self.color_index)
            return GOOGLE_CALENDAR_COLORS['event']['1']

    def save(self, *args, **kwargs):
        if self.name is None:
            self.name = ""
        self.name = self.name[:150]

        if self.description is None:
            self.description = ""
        self.description = self.description[:20000]

        # Validate the color_index field, correct if necessary
        if self.color_index is None or self.color_index == '':
            self.color_index = self.EVENT_COLORS_KEYS[0]
        try:
            assert int(self.color_index) in range(len(self.EVENT_COLORS_KEYS))
        except (ValueError, AssertionError):
            self.color_index = self.EVENT_COLORS_KEYS[0]

        made_aware = False
        if timezone.is_naive(self.start):
            made_aware = True

        self.start = ensure_timezone_awareness(self.start, self.timezone)
        self.end = ensure_timezone_awareness(self.end, self.timezone)

        super(GEvent, self).save(*args, **kwargs)

        if made_aware:
            print "Made datetime timezone aware for GEvent {} with id {}".format(self.name, self.id)

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
    recurring_event_id = models.CharField(max_length=1024, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")

    def __getattr__(self, name):
        if name in set(['created', 'updated']):
            event = GEvent.objects.get(google_id=self.recurring_event_id)
            return getattr(event, 'name')
        else:
            return object.__dict__[name]

    @property
    def created(self):
        event = GEvent.objects.get(google_id=self.recurring_event_id)
        return event.created

    def save(self, *args, **kwargs):

        self.start = ensure_timezone_awareness(self.start)
        self.end = ensure_timezone_awareness(self.end)

        return super(GRecurrence, self).save(*args, **kwargs)


class DeletedEvent(models.Model):

    calendar = models.ForeignKey(GCalendar, related_name='deletedevents')
    original_start_time = models.DateTimeField(null=True)
    google_id = models.CharField(max_length=1024, blank=True, help_text="Unique id per calendar")
    recurring_event_id = models.CharField(max_length=1024, blank=True, help_text="For an instance of a recurring event, the id of the recurring event to which this instance belongs")

    def __str__(self):

        components = []
        if self.google_id:
            components.append("ID {}".format(self.google_id))
        if self.original_start_time:
            components.append("Start {}".format(self.original_start_time))
        if self.recurring_event_id:
            components.append("Recurring id {} ".format(self.recurring_event_id))

        return ", ".join(components)

    def apply(self):
        """
        Ensure that self.calendar is consistent with this DeletedEvent
        """

        if self.original_start_time:
            assert self.recurring_event_id, "If a DeletedEvent has an original_start_time, it must also have a recurring_event_id"
            # Need to add a one hour buffer for this query because this the implementation of RRULE using dateutil uses
            # naive datetimes and therefore doesn't account for daylight savings (not verified, but most likely problem)
            qs = GEvent.objects.filter(calendar=self.calendar,
                                       start__gte=self.original_start_time - timedelta(hours=1),
                                       start__lte=self.original_start_time + timedelta(hours=1),
                                       recurring_event_id=self.recurring_event_id)
            # qs = GEvent.objects.filter(calendar=self.calendar, start=self.original_start_time, recurring_event_id=self.recurring_event_id)
            for event in qs:
                event.delete()

        qs2 = GEvent.objects.filter(calendar=self.calendar, google_id=self.google_id)
        for event in qs2:
            event.delete()


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
