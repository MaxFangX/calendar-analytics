from api.serializers import GCalendarSerializer, GEventSerializer, StatisticSerializer, ColorCategorySerializer, TagSerializer
from cal.helpers import truncated_queryset
from cal.models import ColorCategory, GCalendar, GEvent, Statistic, Profile, Tag
from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils import timezone as timezone_util
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import pytz


@api_view(('GET',))
def api_root(request, format=None):
    # TODO
    return Response({})


@api_view(('GET',))
def sync(request, format=None):

    if not request.user:
        return Response("Not logged in")

    profile = Profile.get_or_create(request.user)[0]

    if request.query_params.get('sync_all'):
        profile.create_calendars(only_primary=False)
        calendars = GCalendar.objects.filter(user=request.user)
    else:
        profile.create_calendars(only_primary=True)
        calendars = [profile.main_calendar]

    for calendar in calendars:
        if request.query_params.get('full_sync'):
            calendar.sync(full_sync=True)
        else:
            calendar.sync()

    return HttpResponseRedirect("/")


class GCalendarList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendars
    """
    serializer_class = GCalendarSerializer

    def get_queryset(self):
        return GCalendar.objects.filter(user=self.request.user)


class GCalendarToggleEnabled(generics.GenericAPIView):
    """
    API endpoint primarily used for toggling calendar defaults
    """
    serializer_class = GCalendarSerializer

    def get_queryset(self):
        return GCalendar.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            calendar = GCalendar.objects.filter(user=request.user).get(id=kwargs['pk'])
        except GCalendar.DoesNotExist:
            raise Exception("Could not find your calendar with primary key {}"
                    .format(kwargs['pk']))

        isNowEnabled = False if calendar.enabled_by_default else True
        calendar.enabled_by_default = isNowEnabled
        calendar.save()

        return Response("Calendar {} is now enabled? {}".format(calendar, isNowEnabled))


class GEventList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendar events, without pruning for duplicates

    Query Parameters

    `start`:      (required) a string representing a date or a datetime
    `end`:        (required) a string representing a date or a datetime
    `calendarId`: (optional) the calendar id from which to pull events. If a calendar id
                  is not supplied, defaults to the user's main calendar.
    `timezone`:   (optional) a string representing a timezone
    `edge`:       (optional) whether events overlapping with the start/end boundaries
                  will be included. Options are 'inclusive', 'exclusive', and 'truncated'.
                  'truncated' means that events that overlap will be included, but will be
                  modified so that they start or end exactly at the boundary they overlap
                  with.
    """
    serializer_class = GEventSerializer

    def get_queryset(self):
        calendar_id = self.request.query_params.get('calendarId')
        start_str = self.request.query_params.get('start')
        end_str = self.request.query_params.get('end')
        timezone_str = self.request.query_params.get('timezone')
        edge_str = self.request.query_params.get('edge')

        calendar = None
        if calendar_id:
            try:
                calendar = GCalendar.objects.filter(user=self.request.user).get(calendar_id=calendar_id)
            except GCalendar.DoesNotExist:
                raise Exception("{} was not a valid calendar id".format(calendar_id))
        else:
            calendar = self.request.user.profile.main_calendar

        qs = GEvent.objects.filter(calendar=calendar)
        qs = qs.exclude(status__in=['tentative', 'cancelled'])

        if not start_str or not end_str:
            raise Exception("Missing query parameter `start` or `end`")

        timezone = None
        if timezone_str:
            try:
                timezone = pytz.timezone(timezone_str)
            except pytz.UnknownTimeZoneError:
                raise Exception("{} could not be parsed into a timezone".format(timezone_str))

        def handle_time_string(time_str):
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

        start = handle_time_string(start_str)
        end = handle_time_string(end_str)

        qs = truncated_queryset(qs, edge_str, start, end)

        return qs


class StatisticList(generics.ListAPIView):
    """
    API endpoint to query for Statistics
    """
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer


class ColorCategoryList(generics.ListAPIView):

    serializer_class = ColorCategorySerializer

    def get_serializer_context(self, *args, **kwargs):
        context = super(ColorCategoryList, self).get_serializer_context(*args, **kwargs)
        context.update({
            'calendar_ids': self.request.query_params.get('calendar_ids'),
            'start': self.request.query_params.get('start'),
            'end': self.request.query_params.get('end')
        })
        return context

    def get_queryset(self):
        return ColorCategory.objects.filter(user=self.request.user)


class ColorCategoryDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ColorCategorySerializer

    def get_serializer_context(self, *args, **kwargs):
        context = super(ColorCategoryDetail, self).get_serializer_context(*args, **kwargs)
        context.update({
            'calendar_ids': self.request.query_params.get('calendar_ids'),
            'start': self.request.query_params.get('start'),
            'end': self.request.query_params.get('end')
        })
        return context

    def get_queryset(self):
        return ColorCategory.objects.filter(user=self.request.user)


class ColorCategoryDetailEvents(generics.ListAPIView):

    serializer_class = GEventSerializer

    def get_queryset(self):
        return ColorCategory.objects.get(user=self.request.user, id=self.kwargs['pk']).query()


class ColorCategoryDetailEventWeek(APIView):

    def get(self, request, *args, **kwargs):
        category = ColorCategory.objects.get(user=self.request.user, id=self.kwargs['pk'])
        return Response(category.get_hours_per_week())


class TagList(generics.ListCreateAPIView):

    serializer_class = TagSerializer

    def get_serializer_context(self):
        return {
            'calendar_ids': self.request.query_params.get('calendar_ids'),
            'start': self.request.query_params.get('start'),
            'end': self.request.query_params.get('end')
        }

    def get_queryset(self):
        qs = Tag.objects.filter(user=self.request.user)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        return qs

    def post(self, request, *args, **kwargs):
        keywords = self.request.data.get('keywords')
        label = self.request.data.get('label')
        if not keywords or not label:
            return Response({'Missing field label or keywords'}, status=status.HTTP_400_BAD_REQUEST)

        tag = Tag()
        tag.user = self.request.user
        tag.keywords = keywords
        tag.label = label
        tag.save()

        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = TagSerializer

    def get_serializer_context(self):
        return {
            'calendar_ids': self.request.query_params.get('calendar_ids'),
            'start': self.request.query_params.get('start'),
            'end': self.request.query_params.get('end')
        }

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)


class TagDetailEvents(generics.ListAPIView):

    serializer_class = GEventSerializer

    def get_queryset(self):
        tag = Tag.objects.get(user=self.request.user, id=self.kwargs['pk'])
        return tag.query()


class TagDetailEventWeek(APIView):

    def get(self, request, *args, **kw):
        tag = Tag.objects.get(user=self.request.user, id=self.kwargs['pk'])
        return Response(tag.get_hours_per_week())
