# Generated by Django 3.2.24 on 2024-02-14 13:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20240214_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 13, 44, 18, 126155, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='tournamentmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 14, 29, 18, 126809, tzinfo=utc)),
        ),
    ]
