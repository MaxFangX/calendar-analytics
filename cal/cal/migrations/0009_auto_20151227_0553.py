# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0008_auto_20151227_0417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='googlecredentials',
            name='id',
            field=models.OneToOneField(related_name='googlecredentials', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
