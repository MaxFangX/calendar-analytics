# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0026_auto_20160324_0516'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gevent',
            old_name='end_timezone',
            new_name='timezone',
        ),
    ]
