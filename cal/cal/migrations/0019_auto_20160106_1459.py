# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0018_auto_20160106_1444'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gevent',
            old_name='recurrent_event_id',
            new_name='recurring_event_id',
        ),
    ]
