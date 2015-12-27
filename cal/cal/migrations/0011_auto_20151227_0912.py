# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0010_auto_20151227_0904'),
    ]

    operations = [
        migrations.RenameField(
            model_name='googlecredentials',
            old_name='id',
            new_name='user',
        ),
    ]
