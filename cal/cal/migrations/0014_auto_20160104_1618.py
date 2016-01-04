# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0013_gcalendar_meta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gevent',
            name='calendar',
        ),
        migrations.DeleteModel(
            name='GEvent',
        ),
    ]
