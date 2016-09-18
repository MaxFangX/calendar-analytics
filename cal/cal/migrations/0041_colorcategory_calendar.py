# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0040_gcalendar_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='colorcategory',
            name='calendar',
            field=models.ForeignKey(related_name='colorcategories', to='cal.GCalendar', null=True),
        ),
    ]
