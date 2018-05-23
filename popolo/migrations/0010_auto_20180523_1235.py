# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-23 10:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('popolo', '0009_auto_20180523_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriginalProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The original profession name', max_length=512, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Original profession',
                'verbose_name_plural': 'Original professions',
            },
        ),
        migrations.AlterModelOptions(
            name='profession',
            options={'verbose_name': 'Normalized profession', 'verbose_name_plural': 'Normalized professions'},
        ),
        migrations.RemoveField(
            model_name='person',
            name='profession',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='parent',
        ),
        migrations.AlterField(
            model_name='profession',
            name='name',
            field=models.CharField(help_text='Normalized profession name', max_length=512, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='originalprofession',
            name='normalized_profession',
            field=models.ForeignKey(blank=True, help_text='The normalized profession', null=True, on_delete=django.db.models.deletion.CASCADE, to='popolo.Profession'),
        ),
        migrations.AddField(
            model_name='person',
            name='original_profession',
            field=models.ForeignKey(blank=True, help_text='The profession of this person, non normalized', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='persons_with_this_profession', to='popolo.OriginalProfession', verbose_name='Profession'),
        ),
    ]
