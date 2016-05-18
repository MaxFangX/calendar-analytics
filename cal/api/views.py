from api.serializers import GEventSerializer, StatisticSerializer, ColorCategorySerializer, TagSerializer
from cal.models import ColorCategory, GEvent, Statistic, Profile, Tag
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


class GEventList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendar events, without pruning for duplicates

    Query Parameters

    `start`:    a string representing a date or a datetime
    `end`:      a string representing a date or a datetime
    `timezone`: a string representing a timezone
    """
    serializer_class = GEventSerializer

    def get_queryset(self):
        qs = GEvent.objects.filter(calendar=self.request.user.profile.main_calendar)
        qs = qs.exclude(status__in=['tentative', 'cancelled'])
        start_str = self.request.query_params.get('start')
        end_str = self.request.query_params.get('end')
        timezone_str = self.request.query_params.get('timezone')

        timezone = None
        if timezone_str:
            try:
                timezone = pytz.timezone(timezone_str)
            except pytz.UnknownTimeZoneError:
                raise pytz.UnknownTimeZoneError("{} could not be parsed into a timezone".format(timezone_str))

        def handle_time_string(time_str):
            was_date = False
            time = parse_datetime(time_str)
            if not time:
                # Parse the date and create a datetime at the zeroth hour
                date = parse_date(time_str)
                if not date:
                    raise Exception("{} couldn't be parsed as date or datetime".format(time_str))
                was_date = True
                time = datetime.combine(date, datetime.min.time())

            if was_date:
                if timezone:
                    time = timezone_util.make_aware(time, timezone)
                else:
                    time = timezone_util.make_aware(time, timezone_util.get_default_timezone())
            else:
                if timezone:
                    time = time.astimezone(pytz.timezone(timezone))
                else:
                    time = time.astimezone(timezone_util.utc)

            return time

        if start_str:
            start = handle_time_string(start_str)
            qs = qs.filter(start__gte=start)
        if end_str:
            end = handle_time_string(end_str)
            qs = qs.filter(end__lte=end)

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
