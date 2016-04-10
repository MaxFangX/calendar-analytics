from cal.models import ColorCategory, GCalendar, GEvent, Statistic, Tag
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)


class GEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = GEvent
        fields = ('id', 'name', 'start', 'end', 'location', 'created', 'updated',
                'calendar', 'id_event', 'i_cal_uid', 'color_index', 'description',
                'status', 'transparency', 'all_day_event', 'timezone',
                'end_time_unspecified', 'recurring_event_id', 'color')
        # color = serializers.SerializerMethodField()

    class GCalendarField(serializers.Field):
        def to_representation(self, obj):
            return {
                'calendar_id': obj.calendar_id,
            }
        def to_internal_value(self, data):
            try:
                return GCalendar.objects.get(calendar_id=data)
            except GCalendar.DoesNotExist:
                return {}

    calendar = GCalendarField(read_only=True, required=False)


class StatisticSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Statistic
        fields = ('name', 'start_time', 'end_time')


class ColorCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ColorCategory
        fields = ('color', 'label')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'user', 'label', 'keywords')

    user = UserSerializer(read_only=True)

