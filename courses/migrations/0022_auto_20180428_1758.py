# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-28 17:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_filter_number_of_courses'),
    ]

    operations = [
        migrations.RenameField(
            model_name='filter',
            old_name='ten_am',
            new_name='after_ten_am',
        ),
    ]
