# Generated by Django 3.2.24 on 2024-02-20 09:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0024_auto_20240219_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 9, 45, 29, 932882, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='tournamentmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 10, 30, 29, 933999, tzinfo=utc)),
        ),
    ]
