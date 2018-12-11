# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-11 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("popolo", "0004_auto_20180716_1639")]

    operations = [
        migrations.AlterField(
            model_name="keyevent",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("ELE", "Election round"),
                    ("ITL", "IT legislature"),
                    ("EUL", "EU legislature"),
                    ("XAD", "External administration"),
                ],
                default="ELE",
                help_text="The electoral type, e.g.: election, legislature, ...",
                max_length=3,
                verbose_name="event type",
            ),
        ),
        migrations.AlterField(
            model_name="keyevent",
            name="identifier",
            field=models.CharField(
                blank=True,
                help_text="An issued identifier",
                max_length=512,
                null=True,
                verbose_name="identifier",
            ),
        ),
    ]
