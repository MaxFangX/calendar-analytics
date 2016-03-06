# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0023_auto_20160131_0226'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color', models.CharField(max_length=100)),
                ('label', models.CharField(max_length=100)),
                ('user', models.ForeignKey(related_name='colorcategories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='usercategory',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserCategory',
        ),
    ]
