# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-27 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='timestamp')),
                ('temperature', models.FloatField(verbose_name='temperature')),
                ('humidity', models.FloatField(verbose_name='humidity')),
                ('weight', models.FloatField(verbose_name='weight')),
            ],
        ),
        migrations.CreateModel(
            name='Scale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(auto_created=True, verbose_name='Token')),
                ('name', models.CharField(max_length=15, verbose_name='Name')),
            ],
        ),
        migrations.AddField(
            model_name='measurement',
            name='scale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataCollector.Scale'),
        ),
    ]