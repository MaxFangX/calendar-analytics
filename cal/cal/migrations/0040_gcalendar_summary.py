# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0039_auto_20160517_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcalendar',
            name='summary',
            field=models.CharField(default='Run this in shell: [cal.update_meta() for cal in GCalendar.objects.all()]', help_text=b'Title of the calendar', max_length=250),
            preserve_default=False,
        ),
    ]
