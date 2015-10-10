from cal.models import GEvent, Statistic
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GEventSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = GEvent
        fields = ('name', 'start_time', 'end_time', 'color', 'note')


class StatisticSerializer:
    
    class Meta:
        model = Statistic
        fields = ('name', 'start_time', 'end_time')
