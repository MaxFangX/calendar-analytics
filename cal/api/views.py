from api.serializers import GCalendarSerializer, GEventSerializer, StatisticSerializer, ColorCategorySerializer, TagSerializer
from cal.models import ColorCategory, GCalendar, GEvent, Statistic, Profile, Tag
from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils import timezone as timezone_util
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import pytz


@api_view(('GET',))
def api_root(request, format=None):
    # TODO
    return Response({})


@api_view(('GET',))
def sync(request, format=None):

    if request.user:
        main_calendar = Profile.get_or_create(request.user)[0].main_calendar
        if main_calendar:
            if request.query_params.get('full_sync'):
                main_calendar.sync(full_sync=True)
            else:
                main_calendar.sync()
            return HttpResponseRedirect("/")

    return Response("Failed to sync calendar")


class GCalendarList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendars
    """
    serializer_class = GCalendarSerializer

    def get_queryset(self):
        return GCalendar.objects.filter(user=self.request.user)


class GEventList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendar events, without pruning for duplicates

    Query Parameters

    `start`:    (required) a string representing a date or a datetime
    `end`:      (required) a string representing a date or a datetime
    `calendar`  (optional) the calendar id from which to pull events. If a calendar id
                is not supplied, defaults to the user's main calendar.
    `timezone`: (optional) a string representing a timezone
    `edge`:     (optional) whether events overlapping with the start/end boundaries
                will be included. Options are 'inclusive', 'exclusive', and 'truncated'.
                'truncated' means that events that overlap will be included, but will be
                modified so that they start or end exactly at the boundary they overlap
                with.
    """
    serializer_class = GEventSerializer

    def get_queryset(self):
        EDGE_OPTIONS = set(['inclusive', 'exclusive', 'truncated'])

        calendar_id = self.request.query_params.get('calendarId')
        start_str = self.request.query_params.get('start')
        end_str = self.request.query_params.get('end')
        timezone_str = self.request.query_params.get('timezone')
        edge_str = self.request.query_params.get('edge')

        calendar = None
        if calendar_id:
            try:
                calendar = GCalendar.objects.filter(self.request.user).get(calendar_id=calendar_id)
            except GCalendar.DoesNotExist:
                raise Exception("{} was not a valid calendar id".format(calendar_id))
        else:
            calendar = self.request.user.profile.main_calendar

        qs = GEvent.objects.filter(calendar=calendar)
        qs = qs.exclude(status__in=['tentative', 'cancelled'])

        edge = None
        if edge_str:
            if edge_str not in EDGE_OPTIONS:
                raise Exception("Edge query parameter {} is not one of {}".format(edge_str, EDGE_OPTIONS))
            edge = edge_str

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
        if edge == 'truncated':
            start_edge = list(qs.filter(start__lt=start, end__gt=start).order_by('start'))
            exclusive = list(qs.filter(start__gte=start, end__lte=end).order_by('start'))
            end_edge = list(qs.filter(start__lt=end, end__gt=end).order_by('start'))
            for s in start_edge:
                s.start = start
            for e in end_edge:
                e.end = end
            qs = start_edge + exclusive + end_edge
        elif edge == 'exclusive':
            qs = qs.filter(start__gte=start, end__lte=end).order_by('start')
        elif edge == 'inclusive' or not edge:
            qs = qs.filter(end__gt=start, start__lt=end).order_by('start')

        return qs


class StatisticList(generics.ListAPIView):
    """
    API endpoint to query for Statistics
    """
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer


class ColorCategoryList(generics.ListAPIView):

    serializer_class = ColorCategorySerializer

    def get_queryset(self):
        return ColorCategory.objects.filter(user=self.request.user)


class TagList(generics.ListCreateAPIView):
    
    serializer_class = TagSerializer

    def get_queryset(self):
        qs = Tag.objects.filter(user=self.request.user)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            qs = qs.filter(start__gte=start)
        if end:
            qs = qs.filter(end__lte=end)

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

        # TODO return serialized object
        return Response({'Successfully created tag!'}, status=status.HTTP_201_CREATED)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)
