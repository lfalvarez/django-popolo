# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-16 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0003_auto_20180710_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='label',
            field=models.CharField(blank=True, help_text='A label describing the membership', max_length=512, null=True, verbose_name='label'),
        ),
    ]
