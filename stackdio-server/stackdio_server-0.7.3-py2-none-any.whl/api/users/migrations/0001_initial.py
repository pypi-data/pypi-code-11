# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('public_key', models.TextField(blank=True)),
                ('user', models.OneToOneField(related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User settings',
            },
        ),
    ]
