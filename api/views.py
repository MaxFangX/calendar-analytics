from api.serializers import GEventSerializer, StatisticSerializer
from cal.models import GEvent, Statistic
from rest_framework import generics


class GEventList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendar events
    """
    queryset = GEvent.objects.all().order_by('start_time')
    serializer_class = GEventSerializer


class StatisticList(generics.ListAPIView):
    """
    API endpoint to query for Statistics
    """
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer
