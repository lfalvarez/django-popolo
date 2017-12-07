# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-07 18:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0003_auto_20171206_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birth_location',
            field=models.CharField(blank=True, help_text='Birth location as a string', max_length=128, null=True, verbose_name='birth location'),
        ),
        migrations.AddField(
            model_name='person',
            name='birth_location_area',
            field=models.ForeignKey(blank=True, help_text='The geographic area corresponding to the birth location', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='persons_born_here', to='popolo.Area', verbose_name='birth location Area'),
        ),
    ]
