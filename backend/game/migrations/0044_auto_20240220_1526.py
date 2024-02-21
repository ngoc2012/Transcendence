# Generated by Django 3.2.24 on 2024-02-20 15:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0043_auto_20240220_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 15, 41, 48, 152460, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='tournamentmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 16, 26, 48, 153554, tzinfo=utc)),
        ),
    ]
