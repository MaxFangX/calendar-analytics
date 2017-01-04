from cal.constants import GOOGLE_CALENDAR_COLORS
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone as timezone_util
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

import json
import pytz


def json_response(data, status=200):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), status=status, content_type="application/json")


def ensure_timezone_awareness(dt, optional_timezone=None):
    """
    Ensures that a datetime is timezone aware, and strips off seconds and microseconds.
    `dt`: the datetime
    `optional_timezone`: string representation of a timezone
    """
    if timezone_util.is_naive(dt):
        if optional_timezone:
            dt = timezone_util.make_aware(dt, pytz.timezone(optional_timezone))
        else:
            dt = timezone_util.make_aware(dt, timezone_util.get_default_timezone())
    dt = dt.astimezone(timezone_util.utc)
    # Remove seconds and microseconds
    dt = dt.replace(second=0, microsecond=0)
    return dt


def handle_time_string(time_str, timezone_str):
    """
    If timezone_str exists get the corresponding timezone. Parses time_str
    and if there is no time, create an event at 0th hour.
    Makes timezone aware if unaware then converts to corresponding timezone.
    """
    timezone = None
    if timezone_str:
        try:
            timezone = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            raise Exception("{} could not be parsed into a timezone".format(timezone_str))

    time = parse_datetime(time_str)
    if not time:
        # Parse the date and create a datetime at the zeroth hour
        date = parse_date(time_str)
        if not date:
            raise Exception("{} couldn't be parsed as date or datetime".format(time_str))
        time = datetime.combine(date, datetime.min.time())

    if timezone_util.is_naive(time):
        if timezone:
            time = timezone_util.make_aware(time, timezone)
        else:
            time = timezone_util.make_aware(time, timezone_util.get_default_timezone())

    if timezone:
        time = time.astimezone(timezone)
    else:
        time = time.astimezone(timezone_util.utc)

    return time


def get_time_series(model, timezone='UTC', time_step='week', calendar_ids=None, start=None, end=None):
    """
    Returns a list of week-hour tuples corresponding to the events in the `model`. Takes in
    timezone in order to accurately aggregate events. Includes time_step input either `daily`,
    `weekly`, or `monthly` which will aggregate accordingly. Splices events that overlap times.
    """
    week_hours = []
    events = model.query(calendar_ids, start, end).order_by('start')
    i = 0
    # Convert start to local time
    start = events[0].start.astimezone(pytz.timezone(timezone))
    if time_step == 'day':
        # To indicate do nothing if Daily is passed in
        pass
    if time_step == 'week':
        # Change start date to be Monday beginning of week
        while start.weekday() != 0:
            start = start - timedelta(days=1)
    if time_step == 'month':
        # Change start date to beginning of month
        while start.day != 1:
            start = start - timedelta(days=1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    # Convert back to UTC
    start = start.astimezone(pytz.utc)
    # Rollover takes care of events that overlap time periods
    rollover = 0
    while i < len(events):
        if time_step == 'day':
            end = start + relativedelta(days=1)
        if time_step == 'week':
            end = start + relativedelta(days=7)
        if time_step == 'month':
            end = start + relativedelta(months=1)
        # Deal with daylight savings time
        if end.astimezone(pytz.timezone(timezone)).hour != 0:
            end = end + timedelta(hours=1)
        total = rollover
        rollover = 0
        while i < len(events) and (end - events[i].start).total_seconds() >= 0:
            # Overlapping events
            if (end - events[i].end).total_seconds() < 0:
                total += (end - events[i].start).total_seconds() / 3600
                rollover = (events[i].end - end).total_seconds() / 3600
            else:
                total += (events[i].end - events[i].start).total_seconds() / 3600
            i += 1
        week_hours.append((start, total))
        start = end
    return week_hours


EDGE_OPTIONS = set(['inclusive', 'exclusive', 'truncated'])
def truncated_queryset(queryset, edge, start, end):
    """
    Takes in a QuerySet and returns the final Iterable(List) of Events.

    `edge`: Whether events overlapping with the start/end boundaries
            will be included. Options are 'inclusive', 'exclusive', and 'truncated'.
            'truncated' means that events that overlap will be included, but will be
            modified so that they start or end exactly at the boundary they overlap
            with.
    """
    from cal.models import InvalidParameterException

    if edge not in EDGE_OPTIONS:
        raise InvalidParameterException("Edge query parameter {} is not one of {}".format(edge, EDGE_OPTIONS))

    if edge == 'truncated':
        start_edge = list(queryset.filter(start__lt=start, end__gt=start).order_by('start'))
        exclusive = list(queryset.filter(start__gte=start, end__lte=end).order_by('start'))
        end_edge = list(queryset.filter(start__lt=end, end__gt=end).order_by('start'))
        for s in start_edge:
            s.start = start
        for e in end_edge:
            e.end = end
        queryset = start_edge + exclusive + end_edge
    elif edge == 'exclusive':
        queryset = queryset.filter(start__gte=start, end__lte=end).order_by('start')
    elif edge == 'inclusive' or not edge:
        queryset = queryset.filter(end__gt=start, start__lt=end).order_by('start')

    return queryset


def get_color(calendar, color_index):
    """
    Takes in a calendar and a color_index and returns the associated color codes
    from constants.py.
    """
    if color_index == "1" and calendar:
        return GOOGLE_CALENDAR_COLORS['calendar'].get(calendar.color_index)
    else:
        return GOOGLE_CALENDAR_COLORS['event'].get(color_index)


class EventCollection:
    """
    Represents a Set of events
    """

    def __init__(self, events_func=None, name=None):
        if events_func:
            self._events_func = events_func
        else:
            self._events_func = lambda: set([])

        self._name = name if name else "EventCollection"

    def get_events(self):
        """
        Returns a set of events.
        """
        return self._events_func()

    def intersection(self, other):

        def lazy_get_events():
            return set.intersection(self.get_events(), other.get_events())

        ec = EventCollection(events_func=lazy_get_events, name="({} intersection {})".format(self, other))

        return ec

    def union(self, other):

        def lazy_get_events():
            return set.union(self.get_events(), other.get_events())

        ec = EventCollection(events_func=lazy_get_events, name="({} union {})".format(self, other))

        return ec

    def total_time(self, calendar=None):

        events = self.get_events()

        total = timedelta()
        for e in events:
            total += e.end - e.start

        return int(total.total_seconds())


class TimeNodeChain(EventCollection):

    """
    A data structure that functions as a wrapper around a linked list of TimeNodes.
    It represents how someone is spending their time at different events. And since
    no one can be at two events at the same time, TimeNodes will overwrite any
    conflicting TimeNodes on insert.
    """

    def __init__(self, timenodes=None):
        """
        Initializes a TimeNodeChain, and, if supplied, inserts an iterable of timenodes.
        """
        self.head = None
        self._length = None
        self._total_time = None
        if timenodes:
            self.insert_all(timenodes)
        self.length

    def get_events(self):
        events = set()
        current = self.get_head()
        while current:
            events.add(current)
            current = current.next

        return events

    def get_head(self):
        return self.head

    @property
    def length(self):
        if not self._length:
            current = self.get_head()
            self._length = 0
            while current:
                self._length += 1
                current = current.next
        return self._length

    @property
    def total_time(self):
        """
        Returns the total time in seconds in this TimeNodeChain.
        Overrides EventCollection.total_time with memoized version
        """
        if not self._total_time:
            total = timedelta()
            current = self.get_head()
            while current and current.next:
                total += current.end - current.start
                current = current.next

            self._total_time = total.total_seconds()

        return self._total_time

    def insert(self, timenode, return_overwrites=False):
        """
        Inserts a single TimeNode in O(n) time and returns the inserted node.
        If return_overwrites is set to True, a set of overwritten nodes will be returned as well.
        Wrapper function for TimeNode.insert, so that TimeNodeChain().insert(node) mutates the chain object
        """
        if self.head:
            current = self.head.insert(timenode)
            while current.prev:
                current = current.prev
            self.head = current

        else:
            self.head = timenode

        self._length = None
        self._total_time = None

        return timenode

    def insert_all(self, timenodes, return_overwrites=False):
        """
        Inserts an iterable of TimeNodes (list, QuerySet).
        If return_overwrites is set to True, a set of overwritten nodes will be returned
        If the list is ordered by start time, this operation will take roughly O(n)
        """
        if len(timenodes) == 0:
            return

        # Add the first node to avoid erroring on None.insert
        if self.head:
            last = self.head
            last.insert(timenodes[0])
        else:
            self.head = timenodes[0]
            last = self.head

        for i in range(1, len(timenodes)):
            node = timenodes[i]
            last.insert(node)
            last = node

        while last.prev:
            last = last.prev
        self.head = last

        self.length
        self.total_time

    def get_inverse(self):
        """
        Returns a TimeNodeChain representing the gaps between TimeNodes

        Example: If a TimeNode chain has nodes 1-2, 3-4, 5-6, 6-9,
        get_inverse() returns a chain with nodes 2-3, 4-5
        """
        # TODO use this somewhere to encourage completeness
        if not self.head:
            return None

        current = self.head
        chain = TimeNodeChain()
        last = None
        while current.next:
            if current.end == current.next.start:
                current = current.next
                continue
            elif current.end > current.next.start:
                raise Exception("Inconsistent start and end times between TimeNodes {} and {}".
                        format(current.id, current.next.id))

            node = TimeNode(current.end, current.next.start, "GAP: {}--{}".format(current.id, current.next.id))
            if last:
                last.insert(node)
            else:
                chain.insert(node)
                last = node

            current = current.next

        return chain

    def __str__(self):
        if not self.head:
            return "<Empty TimeNodeChain>"
        else:
            current = self.head
            counter = 0
            result = ""
            while current.next and counter < 10:
                result += "<{}>".format(current.id)
                current = current.next
                counter += 1
            return result


class TimeNode:
    """
    Class representing a block of time.
    """

    def __init__(self, start, end, id=None):
        self.id = id
        self.prev = None
        self.next = None
        self.start = start
        self.end = end

    def insert(self, timenode, return_overwrites=False):
        """
        Inserts a single TimeNode in O(n) time and returns the current node.
        """

        # Basic sanity chex
        if timenode.prev:
            print "Warning! Timenode '{}' to be inserted has a prev".format(timenode.id)
        if timenode.next:
            print "Warning! Timenode '{}' to be inserted has a next".format(timenode.id)
        if not timenode.start or not timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")

        def try_insert(node):
            if not node.start or not node.end or node.start > node.end:
                raise Exception("Base node missing start or end time, or start time > end time")
            if timenode.start >= node.end:
                if node.next:
                    # Handle the case of a "sandwiched" node
                    if node.next.start >= timenode.end:
                        node.next.prev = timenode
                        timenode.next = node.next
                        node.next = timenode
                        timenode.prev = node
                    else:
                        return False, node.next
                else:
                    if timenode.prev:
                        print "Warning! Overwriting timenode.prev"
                    node.next = timenode
                    timenode.prev = node
                return True, None
            elif timenode.end <= node.start:
                if node.prev:
                    # Handle the case of a "sandwiched" node
                    if node.prev.end <= timenode.start:
                        node.prev.next = timenode
                        timenode.prev = node.prev
                        node.prev = timenode
                        timenode.next = node
                    else:
                        return False, node.prev
                else:
                    if timenode.next:
                        print "Warning! Overwriting timenode.next of timenode '{}'".format(timenode.id)
                    node.prev = timenode
                    timenode.next = node
                return True, None
            else:
                # Remove the current node
                if node.prev:
                    node.prev.next = node.next
                if node.next:
                    node.next.prev = node.prev
                # Recurse; call insert on an adjacent node or return node
                if node.next:
                    return False, node.next
                elif node.prev:
                    return False, node.prev
                return True, None

        inserted = None
        next_node = self
        while not inserted:
            inserted, next_node = try_insert(next_node)

        return timenode

    def old_insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the current node.
        """
        # TODO make this return the inserted node

        # Basic sanity chex
        if not self.start or not self.end or self.start > self.end:
            raise Exception("Base node missing start or end time, or start time > end time")
        if not timenode.start or not timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")
        if timenode.prev:
            print "Warning! Timenode '{}' to be inserted has a prev".format(timenode.id)
        if timenode.next:
            print "Warning! Timenode '{}' to be inserted has a next".format(timenode.id)

        if timenode.start >= self.end:
            if self.next:
                # Handle the case of a "sandwiched" node
                if self.next.start >= timenode.end:
                    self.next.prev = timenode
                    timenode.next = self.next
                    self.next = timenode
                    timenode.prev = self
                else:
                    self.next = self.next.insert(timenode)
                    self.next.prev = self
            else:
                if timenode.prev:
                    print "Warning! Overwriting timenode.prev"
                self.next = timenode
                timenode.prev = self
            return self
        elif timenode.end <= self.start:
            if self.prev:
                # Handle the case of a "sandwiched" node
                if self.prev.end <= timenode.start:
                    self.prev.next = timenode
                    timenode.prev = self.prev
                    self.prev = timenode
                    timenode.next = self
                else:
                    self.prev = self.prev.insert(timenode)
                    self.prev.next = self
            else:
                if timenode.next:
                    print "Warning! Overwriting timenode.next of timenode '{}'".format(timenode.id)
                self.prev = timenode
                timenode.next = self
            return self
        else:
            # Remove the current node
            if self.prev:
                self.prev.next = self.next
            if self.next:
                self.next.prev = self.prev

            # Recurse; call insert on an adjacent node or return self
            if self.next:
                self.next.insert(timenode)
            elif self.prev:
                self.prev.insert(timenode)

            return timenode
