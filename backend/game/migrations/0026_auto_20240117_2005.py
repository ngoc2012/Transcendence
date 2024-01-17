# Generated by Django 3.2.12 on 2024-01-17 20:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0025_auto_20240117_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 17, 20, 20, 52, 944069, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='roomsmodel',
            name='score1',
            field=models.IntegerField(default=0),
        ),
    ]
