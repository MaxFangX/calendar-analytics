from api.serializers import GEventSerializer, StatisticSerializer, ColorCategorySerializer
from cal.models import ColorCategory, GEvent, Statistic, Profile
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
            return Response("Successfully synced Calendar.")

    return Response("Failed to sync calendar")


class GEventList(generics.ListAPIView):
    """
    API endpoint to query for Google Calendar events, without pruning for duplicates
    """
    serializer_class = GEventSerializer

    def get_queryset(self):
        qs = GEvent.objects.filter(calendar=self.request.user.profile.main_calendar)
        qs = qs.exclude(status__in=['tentative', 'cancelled'])
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
        return ColorCategory.objects.filter(user=self.request.user)
