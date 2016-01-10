# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0020_auto_20160107_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistic',
            name='display_name',
        ),
        migrations.AlterField(
            model_name='statistic',
            name='end_time',
            field=models.DateTimeField(help_text=b'The ending point for this statistic', null=True),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='name',
            field=models.CharField(help_text=b'The name of the statistic ', max_length=100),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='start_time',
            field=models.DateTimeField(help_text=b'The starting point for this statistic', null=True),
        ),
    ]
