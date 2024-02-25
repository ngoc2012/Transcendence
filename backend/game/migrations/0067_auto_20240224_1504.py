# Generated by Django 3.2.24 on 2024-02-24 15:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0066_auto_20240224_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 24, 15, 19, 15, 947725, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='tournamentroomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 24, 15, 19, 15, 949589, tzinfo=utc)),
        ),
    ]
