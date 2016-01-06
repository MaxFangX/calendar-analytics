# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0016_auto_20160106_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gevent',
            name='color',
            field=models.CharField(blank=True, max_length=10, choices=[(b'11', b'11'), (b'10', b'10'), (b'1', b'1'), (b'3', b'3'), (b'2', b'2'), (b'5', b'5'), (b'4', b'4'), (b'7', b'7'), (b'6', b'6'), (b'9', b'9'), (b'8', b'8')]),
        ),
    ]
