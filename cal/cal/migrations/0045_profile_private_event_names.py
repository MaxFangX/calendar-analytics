# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0044_gcalendar_enabled_by_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='private_event_names',
            field=models.BooleanField(default=False, help_text=b"If the user's event names will return as dummy text."),
        ),
    ]
