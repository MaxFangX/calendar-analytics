# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0014_auto_20160104_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='GEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'(No name)', max_length=150, blank=True)),
                ('start', models.DateTimeField(help_text=b'When the event started. 12AM for all day events')),
                ('end', models.DateTimeField(help_text=b'When the event ended. 12AM the next day for all day events')),
                ('location', models.CharField(help_text=b'Geographic location as free form text', max_length=500, blank=True)),
                ('created', models.DateTimeField(help_text=b'When the event was created, on Google')),
                ('updated', models.DateTimeField(help_text=b'When the event was last updated, on Google')),
                ('color', models.CharField(max_length=10, choices=[(b'11', b'#dc2127'), (b'10', b'#51b749'), (b'1', b'#a4bdfc'), (b'3', b'#dbadff'), (b'2', b'#7ae7bf'), (b'5', b'#fbd75b'), (b'4', b'#ff887c'), (b'7', b'#46d6db'), (b'6', b'#ffb878'), (b'9', b'#5484ed'), (b'8', b'#e1e1e1')])),
                ('id_event', models.CharField(help_text=b'Unique id per calendar', max_length=1024)),
                ('i_cal_uid', models.CharField(help_text=b'Unique id across calendaring systems. Only 1 per recurring event', max_length=1024)),
                ('description', models.TextField(max_length=20000, blank=True)),
                ('status', models.CharField(default=b'confirmed', max_length=50, blank=True, choices=[(b'confirmed', b'Confirmed'), (b'tentative', b'Tentative'), (b'cancelled', b'Cancelled')])),
                ('transparency', models.CharField(default=b'opaque', help_text=b'Whether the event blocks time on the calendar.', max_length=50, blank=True, choices=[(b'opaque', b'Opaque - The event blocks time on the calendar'), (b'transparent', b'Transparent - The event does not block time on the calendar')])),
                ('recurrent_event_id', models.CharField(help_text=b'For an instance of a recurring event, the id of the recurring event to which this instance belongs', max_length=1024, blank=True)),
                ('all_day_event', models.BooleanField(default=False)),
                ('end_timezone', models.CharField(help_text=b'IANA Time Zone Database Name', max_length=200, blank=True)),
                ('end_time_unspecified', models.BooleanField(default=False, help_text=b'If an end time is actually unspecified, since an end time is always specified for compatibility reasons')),
                ('calendar', models.ForeignKey(to='cal.GCalendar')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
