# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0021_auto_20160110_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='analysis_start',
            field=models.DateTimeField(help_text=b"When the analysis of the user's calendar will start", null=True, blank=True),
        ),
    ]
