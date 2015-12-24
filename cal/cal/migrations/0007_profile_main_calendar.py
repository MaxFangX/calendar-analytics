# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0006_googlecredentials_googleflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='main_calendar',
            field=models.ForeignKey(to='cal.GCalendar', null=True),
        ),
    ]
