# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0009_auto_20151227_0553'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcalendar',
            name='calendar_id',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='googlecredentials',
            name='next_sync_token',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
