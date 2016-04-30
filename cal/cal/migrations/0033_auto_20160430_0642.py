# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0032_tag_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grecurrence',
            name='parent',
        ),
        migrations.DeleteModel(
            name='GRecurrence',
        ),
    ]
