# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0012_profile_authed'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcalendar',
            name='meta',
            field=jsonfield.fields.JSONField(default=b'{}', blank=True),
        ),
    ]
