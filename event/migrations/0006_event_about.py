# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-30 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_event_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='about',
            field=models.TextField(blank=True, null=True),
        ),
    ]
