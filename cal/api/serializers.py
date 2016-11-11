from cal.models import ColorCategory, GCalendar, GEvent, Statistic, Tag
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)


class GCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = GCalendar
        fields = ('id', 'calendar_id', 'meta', 'summary', 'enabled_by_default')


class GEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = GEvent
        fields = ('id', 'name', 'start', 'end', 'location', 'created', 'updated',
                  'calendar', 'google_id', 'i_cal_uid', 'color_index', 'description',
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

    hours = serializers.SerializerMethodField()

    def get_fields(self, *args, **kwargs):
        fields = super(ColorCategorySerializer, self).get_fields(*args, **kwargs)
        fields['calendar'].queryset = fields['calendar'].queryset.filter(user=self.context['request'].user)
        return fields

    class Meta:
        model = ColorCategory
        fields = ('id', 'color_index', 'label', 'hours', 'calendar')

    def get_hours(self, obj):
        calendar_ids = self.context['calendar_ids']
        start = self.context['start']
        end = self.context['end']
        return obj.hours(calendar_ids=calendar_ids, start=start, end=end)


class TagSerializer(serializers.ModelSerializer):

    hours = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'label', 'keywords', 'hours')

    def get_hours(self, obj):
        calendar_ids = self.context.get('calendar_ids')
        start = self.context.get('start')
        end = self.context.get('end')
        return obj.hours(calendar_ids=calendar_ids, start=start, end=end)
