from cal.models import ColorCategory, GEvent, Statistic
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = GEvent
        fields = ('name', 'start', 'end', 'location', 'created', 'updated')


class StatisticSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Statistic
        fields = ('name', 'start_time', 'end_time')


class ColorCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ColorCategory
        fields = ('color', 'label')
