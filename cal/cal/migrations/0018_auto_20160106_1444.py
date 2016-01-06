# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0017_auto_20160106_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gevent',
            name='color',
            field=models.CharField(blank=True, max_length=10, choices=[(b'11', b'#dc2127'), (b'10', b'#51b749'), (b'1', b'#a4bdfc'), (b'3', b'#dbadff'), (b'2', b'#7ae7bf'), (b'5', b'#fbd75b'), (b'4', b'#ff887c'), (b'7', b'#46d6db'), (b'6', b'#ffb878'), (b'9', b'#5484ed'), (b'8', b'#e1e1e1')]),
        ),
    ]
