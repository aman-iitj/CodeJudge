# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20150406_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='inputFormat',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
