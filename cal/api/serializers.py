from cal.models import Category, GCalendar, GEvent, Statistic, Tag
from django.contrib.auth.models import User
from rest_framework import serializers
from cal.helpers import handle_time_string

import ast

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)


class GCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = GCalendar
        fields = ('id', 'calendar_id', 'meta', 'summary', 'enabled_by_default')


class GEventSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = GEvent
        fields = ('id', 'name', 'start', 'end', 'location', 'created', 'updated',
                  'calendar', 'google_id', 'i_cal_uid', 'color_index', 'description',
                  'status', 'transparency', 'all_day_event', 'timezone',
                  'end_time_unspecified', 'recurring_event_id', 'color')
        # color = serializers.SerializerMethodField()

    def get_name(self, obj):
        if self.context['request'].user.profile.private_event_names:
            return "EECS EECS EECS"
        return obj.name

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


class CategorySerializer(serializers.ModelSerializer):

    hours = serializers.SerializerMethodField()
    category_color = serializers.SerializerMethodField()

    def get_fields(self, *args, **kwargs):
        fields = super(CategorySerializer, self).get_fields(*args, **kwargs)
        fields['calendar'].queryset = fields['calendar'].queryset.filter(user=self.context['request'].user)
        return fields

    class Meta:
        model = Category
        fields = ('id', 'label', 'hours', 'calendar', 'category_color')

    def get_hours(self, obj):
        if self.context.get('calendar_ids') is not None:
            # literal_evel converts str representation of list into Python list
            calendar_ids = ast.literal_eval(self.context['calendar_ids'])
        else:
            calendar_ids = []
        start = self.context['start']
        end = self.context['end']
        timezone = self.context['timezone']
        if start:
            start = handle_time_string(start, timezone)
        if end:
            end = handle_time_string(end, timezone)
        return obj.hours(calendar_ids=calendar_ids, start=start, end=end)

    def get_category_color(self, obj):
        return obj.category_color()


class TagSerializer(serializers.ModelSerializer):

    hours = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'label', 'keywords', 'hours')

    def get_hours(self, obj):
        if self.context.get('calendar_ids') is not None:
            calendar_ids = ast.literal_eval(self.context['calendar_ids'])
        else:
            calendar_ids = []
        start = self.context.get('start')
        end = self.context.get('end')
        timezone = self.context.get('timezone')
        if start:
            start = handle_time_string(start, timezone)
        if end:
            end = handle_time_string(end, timezone)
        return obj.hours(calendar_ids=calendar_ids, start=start, end=end)


class CategoryTimeSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('timezone')


class TagTimeSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('timezone')
