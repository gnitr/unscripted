# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 21:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('unsccore', '0002_auto_20171019_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='box',
            name='parent',
            field=models.ForeignKey(help_text='Link to the Box that contains this box. Might be null for a World.', null=True, on_delete=django.db.models.deletion.CASCADE, to='unsccore.Box'),
        ),
        migrations.AlterField(
            model_name='thingclass',
            name='module',
            field=models.SlugField(help_text='the name of the python module that contains the management class for this type of thing.', unique=True, verbose_name='Python module'),
        ),
    ]
