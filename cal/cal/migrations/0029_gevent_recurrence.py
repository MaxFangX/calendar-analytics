# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0028_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='gevent',
            name='recurrence',
            field=models.CharField(help_text=b'string representation of list of RRULE, EXRULE, RDATE and EXDATE lines for a recurring event, as specified in RFC5545', max_length=1000, blank=True),
        ),
    ]
