# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0007_profile_main_calendar'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='google_id',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='locale',
            field=models.CharField(default=b'en', max_length=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='picture_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
