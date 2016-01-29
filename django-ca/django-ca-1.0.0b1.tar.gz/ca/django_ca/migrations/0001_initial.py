# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-28 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('expires', models.DateTimeField()),
                ('csr', models.TextField(verbose_name='CSR')),
                ('pub', models.TextField(verbose_name='Public key')),
                ('cn', models.CharField(max_length=64, verbose_name='CommonName')),
                ('serial', models.CharField(max_length=35)),
                ('revoked', models.BooleanField(default=False)),
                ('revoked_date', models.DateTimeField(blank=True, null=True, verbose_name='Revoked on')),
                ('revoked_reason', models.CharField(blank=True, max_length=32, null=True, verbose_name='Reason for revokation')),
            ],
        ),
        migrations.CreateModel(
            name='Watcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='CommonName')),
                ('mail', models.EmailField(max_length=254, verbose_name='E-Mail')),
            ],
        ),
        migrations.AddField(
            model_name='certificate',
            name='watchers',
            field=models.ManyToManyField(blank=True, related_name='certificates', to='django_ca.Watcher'),
        ),
    ]
