# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0035_auto_20160505_0215'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('id_event', models.CharField(help_text=b'Unique id per calendar', max_length=1024, blank=True)),
                ('recurring_event_id', models.CharField(help_text=b'For an instance of a recurring event, the id of the recurring event to which this instance belongs', max_length=1024, blank=True)),
                ('calendar', models.ForeignKey(related_name='deletedevents', to='cal.GCalendar')),
            ],
        ),
    ]
