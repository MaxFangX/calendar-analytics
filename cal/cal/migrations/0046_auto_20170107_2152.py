# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0045_profile_private_event_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color_index', models.CharField(help_text=b'str of the number of the event color in constants.py', max_length=100)),
                ('label', models.CharField(max_length=100)),
                ('calendar', models.ForeignKey(related_name='categories', to='cal.GCalendar', null=True)),
                ('user', models.ForeignKey(related_name='categories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='colorcategory',
            name='calendar',
        ),
        migrations.RemoveField(
            model_name='colorcategory',
            name='user',
        ),
        migrations.DeleteModel(
            name='ColorCategory',
        ),
    ]
