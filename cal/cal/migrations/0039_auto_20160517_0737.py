# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0038_auto_20160513_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gevent',
            name='color_index',
            field=models.CharField(max_length=10, choices=[(b'1', b'#a4bdfc'), (b'2', b'#7ae7bf'), (b'3', b'#dbadff'), (b'4', b'#ff887c'), (b'5', b'#fbd75b'), (b'6', b'#ffb878'), (b'7', b'#46d6db'), (b'8', b'#e1e1e1'), (b'9', b'#5484ed'), (b'10', b'#51b749'), (b'11', b'#dc2127')]),
        ),
    ]
