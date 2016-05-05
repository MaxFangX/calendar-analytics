# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0034_grecurrence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grecurrence',
            name='recurring_event_id',
            field=models.CharField(help_text=b'For an instance of a recurring event, the id of the recurring event to which this instance belongs', max_length=1024),
        ),
    ]
