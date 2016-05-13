# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0036_deletedevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deletedevent',
            name='start',
            field=models.DateTimeField(null=True),
        ),
    ]
