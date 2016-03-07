# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0024_auto_20160306_0429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colorcategory',
            name='color',
            field=models.CharField(help_text=b'str of the number of the event color in constants.py', max_length=100),
        ),
    ]
