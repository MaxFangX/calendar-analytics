# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0041_colorcategory_calendar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='colorcategory',
            old_name='color',
            new_name='color_index',
        ),
    ]
