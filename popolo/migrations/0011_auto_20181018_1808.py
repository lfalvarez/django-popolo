# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-18 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("popolo", "0010_auto_20181012_1704")]

    operations = [
        migrations.AlterField(
            model_name="educationlevel",
            name="name",
            field=models.CharField(
                help_text="Education level name",
                max_length=256,
                unique=True,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="originaleducationlevel",
            name="name",
            field=models.CharField(
                help_text="Education level name",
                max_length=512,
                unique=True,
                verbose_name="name",
            ),
        ),
    ]
