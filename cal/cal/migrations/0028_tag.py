# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0027_auto_20160401_0622'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(help_text=b'The name of this tag', max_length=100)),
                ('keywords', models.CharField(help_text=b'Comma-separated list of strings to search for', max_length=100)),
                ('user', models.ForeignKey(related_name='tags', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
