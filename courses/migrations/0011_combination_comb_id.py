# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-15 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_combination_course_combo'),
    ]

    operations = [
        migrations.AddField(
            model_name='combination',
            name='comb_id',
            field=models.SmallIntegerField(default=-1),
        ),
    ]
