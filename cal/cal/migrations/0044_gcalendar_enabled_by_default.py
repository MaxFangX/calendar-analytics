# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0043_gcalendar_color_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcalendar',
            name='enabled_by_default',
            field=models.BooleanField(default=True),
        ),
    ]
