# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0015_gevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcalendar',
            name='user',
            field=models.ForeignKey(related_name='gcalendars', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='gevent',
            name='calendar',
            field=models.ForeignKey(related_name='gevents', to='cal.GCalendar'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='user',
            field=models.ForeignKey(related_name='statistics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usercategory',
            name='user',
            field=models.ForeignKey(related_name='usercategories', to=settings.AUTH_USER_MODEL),
        ),
    ]
