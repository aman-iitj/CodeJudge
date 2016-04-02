# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20160402_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='hacker',
            name='roll',
            field=models.CharField(default=b'0', max_length=50),
        ),
    ]
