# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-02 23:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20180402_0615'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='evaluation',
            new_name='evals',
        ),
    ]
