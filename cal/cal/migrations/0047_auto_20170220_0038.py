# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0046_auto_20170107_2152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googlecredentials',
            name='next_sync_token',
        ),
        migrations.AddField(
            model_name='gcalendar',
            name='next_sync_token',
            field=models.CharField(help_text=b'The syncToken provided for this specific calendar', max_length=100, null=True, blank=True),
        ),
    ]
