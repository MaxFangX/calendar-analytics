from django.contrib.auth.models import User
from rest_framework import viewsets
from api.serializers import GEventSerializer, UserSerializer
from cal.models import GEvent


class UserList(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GEventList(viewsets.ModelViewSet):
    """
    API endpoint to query for Google Calendar events
    """
    queryset = GEvent.objects.all().order_by('start_time')
    serializer_class = GEventSerializer
