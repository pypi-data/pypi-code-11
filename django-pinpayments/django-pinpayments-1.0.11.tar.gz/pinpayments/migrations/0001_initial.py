# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(help_text='A bank account token provided by Pin', max_length=40, verbose_name='Pin API Bank account token', db_index=True)),
                ('bank_name', models.CharField(help_text='The name of the bank at which this account is held', max_length=100, verbose_name='Bank Name')),
                ('branch', models.CharField(help_text='The name of the branch at which this account is held', max_length=100, verbose_name='Branch name', blank=True)),
                ('name', models.CharField(help_text='The name of the bank account', max_length=100, verbose_name='Recipient Name')),
                ('bsb', models.IntegerField(help_text='The BSB (Bank State Branch) code of the bank account.', verbose_name='BSB')),
                ('number', models.CharField(help_text='The account number of the bank account', max_length=20, verbose_name='BSB')),
                ('environment', models.CharField(help_text='The name of the Pin environment to use, eg test or live.', max_length=25, db_index=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomerToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('environment', models.CharField(help_text='The name of the Pin environment to use, eg test or live.', max_length=25, db_index=True, blank=True)),
                ('token', models.CharField(help_text='Generated by Card API or Customers API', max_length=100, verbose_name='Token')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('card_type', models.CharField(choices=[('master', 'Mastercard'), ('visa', 'Visa')], max_length=20, blank=True, help_text='Determined automatically by Pin', null=True, verbose_name='Card Type')),
                ('card_number', models.CharField(help_text='Cleansed by Pin API', max_length=100, null=True, verbose_name='Card Number', blank=True)),
                ('card_name', models.CharField(max_length=100, null=True, verbose_name='Name on Card', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PinRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(help_text='A recipient token provided by Pin', max_length=40, db_index=True)),
                ('email', models.EmailField(help_text='As passed to Pin.', max_length=100)),
                ('name', models.CharField(help_text='Optional. The name by which the recipient is referenced', max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Time created')),
                ('environment', models.CharField(help_text='The name of the Pin environment to use, eg test or live.', max_length=25, db_index=True, blank=True)),
                ('bank_account', models.ForeignKey(blank=True, to='pinpayments.BankAccount', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PinTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(help_text='Time this transaction was put in the database. May differ from the time that PIN reports the transaction.', verbose_name='Date', db_index=True)),
                ('environment', models.CharField(help_text='The name of the Pin environment to use, eg test or live.', max_length=25, db_index=True, blank=True)),
                ('amount', models.DecimalField(verbose_name='Amount (Dollars)', max_digits=10, decimal_places=2)),
                ('fees', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, blank=True, help_text='Fees charged to you by Pin, for this transaction, in dollars', null=True, verbose_name='Transaction Fees')),
                ('description', models.TextField(help_text='As provided when you initiated the transaction', null=True, verbose_name='Description', blank=True)),
                ('processed', models.BooleanField(default=False, help_text='Has this been sent to Pin yet?', verbose_name='Processed?')),
                ('succeeded', models.BooleanField(default=False, help_text='Was the transaction approved?', verbose_name='Success?')),
                ('currency', models.CharField(default='AUD', help_text='Currency transaction was processed in', max_length=100, verbose_name='Currency')),
                ('transaction_token', models.CharField(max_length=100, blank=True, help_text='Unique ID from Pin for this transaction', null=True, verbose_name='Pin API Transaction Token', db_index=True)),
                ('card_token', models.CharField(help_text='Card token used for this transaction (Card API and Web Forms)', max_length=40, null=True, verbose_name='Pin API Card Token', blank=True)),
                ('pin_response', models.CharField(help_text='Response text, usually Success!', max_length=255, null=True, verbose_name='API Response', blank=True)),
                ('ip_address', models.GenericIPAddressField(help_text='IP Address used for payment')),
                ('email_address', models.EmailField(help_text='As passed to Pin.', max_length=100, verbose_name='E-Mail Address')),
                ('card_address1', models.CharField(help_text='Address entered by customer to process this transaction', max_length=100, null=True, verbose_name='Cardholder Street Address', blank=True)),
                ('card_address2', models.CharField(max_length=100, null=True, verbose_name='Cardholder Street Address Line 2', blank=True)),
                ('card_city', models.CharField(max_length=100, null=True, verbose_name='Cardholder City', blank=True)),
                ('card_state', models.CharField(max_length=100, null=True, verbose_name='Cardholder State', blank=True)),
                ('card_postcode', models.CharField(max_length=100, null=True, verbose_name='Cardholder Postal / ZIP Code', blank=True)),
                ('card_country', models.CharField(max_length=100, null=True, verbose_name='Cardholder Country', blank=True)),
                ('card_number', models.CharField(help_text='Cleansed by Pin API', max_length=100, null=True, verbose_name='Card Number', blank=True)),
                ('card_type', models.CharField(choices=[('master', 'Mastercard'), ('visa', 'Visa')], max_length=20, blank=True, help_text='Determined automatically by Pin', null=True, verbose_name='Card Type')),
                ('pin_response_text', models.TextField(help_text='The full JSON response from the Pin API', null=True, verbose_name='Complete API Response', blank=True)),
                ('customer_token', models.ForeignKey(blank=True, to='pinpayments.CustomerToken', help_text='Provided by Customer API', null=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'PIN.net.au Transaction',
                'verbose_name_plural': 'PIN.net.au Transactions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PinTransfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transfer_token', models.CharField(max_length=100, blank=True, help_text='Unique ID from Pin for this transfer', null=True, verbose_name='Pin API Transfer Token', db_index=True)),
                ('status', models.CharField(help_text='Status of transfer at time of saving', max_length=100, null=True, blank=True)),
                ('currency', models.CharField(help_text='currency of transfer', max_length=10)),
                ('description', models.CharField(help_text='Description as shown on statement', max_length=100, null=True, blank=True)),
                ('amount', models.IntegerField(help_text='Transfer amount, in the base unit of the currency (e.g.: cents for AUD, yen for JPY)')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pin_response_text', models.TextField(help_text='The full JSON response from the Pin API', null=True, verbose_name='Complete API Response', blank=True)),
                ('recipient', models.ForeignKey(blank=True, to='pinpayments.PinRecipient', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
