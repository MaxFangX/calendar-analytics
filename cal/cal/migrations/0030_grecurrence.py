# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0029_gevent_recurrence'),
    ]

    operations = [
        migrations.CreateModel(
            name='GRecurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('parent', models.ForeignKey(related_name='recurrences', to='cal.GEvent')),
            ],
        ),
    ]
