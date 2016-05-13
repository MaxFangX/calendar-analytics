# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0037_auto_20160513_0819'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deletedevent',
            old_name='id_event',
            new_name='google_id',
        ),
        migrations.RenameField(
            model_name='deletedevent',
            old_name='start',
            new_name='original_start_time',
        ),
        migrations.RenameField(
            model_name='gevent',
            old_name='id_event',
            new_name='google_id',
        ),
    ]
