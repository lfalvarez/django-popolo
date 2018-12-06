# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-21 15:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("contenttypes", "0002_remove_content_type_name"), ("popolo", "0006_auto_20180913_1607")]

    operations = [
        migrations.CreateModel(
            name="KeyEventRel",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_id", models.PositiveIntegerField(db_index=True, null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "key_event",
                    models.ForeignKey(
                        help_text="A relation to a KeyEvent instance assigned to this object",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_objects",
                        to="popolo.KeyEvent",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.RemoveField(model_name="organization", name="key_events"),
    ]
