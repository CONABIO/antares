# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('madmex', '0002_auto_20171027_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landsatcatalog',
            name='landsat_product_id',
            field=models.CharField(default=None, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='landsatcatalog',
            name='scene_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
