# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-19 20:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('howl', '0003_alert_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPooling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement', models.IntegerField()),
                ('observer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='howl.Observer')),
            ],
        ),
    ]
