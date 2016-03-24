# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0025_auto_20160307_0914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gevent',
            old_name='color',
            new_name='color_index',
        ),
    ]
