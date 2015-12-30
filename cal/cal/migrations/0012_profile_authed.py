# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0011_auto_20151227_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='authed',
            field=models.BooleanField(default=False, help_text=b"If the user's oauth credentials are currently valid"),
        ),
    ]
