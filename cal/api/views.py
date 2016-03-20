from api.serializers import GEventSerializer, StatisticSerializer, ColorCategorySerializer
from cal.models import ColorCategory, GEvent, Statistic
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(('GET',))
def api_root(request, format=None):
    # TODO
    return Response({})


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

class ColorCategoryList(generics.ListAPIView):

    queryset = ColorCategory.objects.all()
    serializer_class = ColorCategorySerializer
