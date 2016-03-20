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
    serializer_class = GEventSerializer

    def get_queryset(self):
        qs = GEvent.objects.filter(calendar=self.request.user.profile.main_calendar)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            qs = qs.filter(start__gte=start)
        if end:
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
        queryset = ColorCategory.objects.filter(user=self.request.user)
