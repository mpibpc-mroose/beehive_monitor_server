# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-27 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataCollector', '0002_auto_20171227_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scale',
            name='name',
            field=models.CharField(max_length=15, unique=True, verbose_name='Name'),
        ),
    ]
