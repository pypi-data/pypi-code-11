# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-16 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('howl', '0002_auto_20151205_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='value',
            field=models.CharField(default=0, max_length=255, verbose_name='Value'),
            preserve_default=False,
        ),
    ]
