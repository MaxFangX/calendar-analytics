# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('cal', '0004_statistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='display_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gevent',
            name='color',
            field=models.CharField(max_length=10, choices=[(b'11', b'#dc2127'), (b'10', b'#51b749'), (b'1', b'#a4bdfc'), (b'3', b'#dbadff'), (b'2', b'#7ae7bf'), (b'5', b'#fbd75b'), (b'4', b'#ff887c'), (b'7', b'#46d6db'), (b'6', b'#ffb878'), (b'9', b'#5484ed'), (b'8', b'#e1e1e1')]),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
    ]
