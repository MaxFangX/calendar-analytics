# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0031_taggroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='group',
            field=models.ForeignKey(related_name='tags', default=None, to='cal.TagGroup', null=True),
        ),
    ]
