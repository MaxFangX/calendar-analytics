# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0022_profile_analysis_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gevent',
            name='end_timezone',
            field=models.CharField(help_text=b'IANA Time Zone Database Name', max_length=200, null=True, blank=True),
        ),
    ]
