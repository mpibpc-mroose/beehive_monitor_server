# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-30 20:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataCollector', '0003_auto_20171227_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='pressure',
            field=models.PositiveIntegerField(default=1000, verbose_name='Pressure'),
        ),
    ]
