# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0019_auto_20160106_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gevent',
            name='name',
            field=models.CharField(default=b'(No title)', max_length=150, blank=True),
        ),
    ]
