# Generated by Django 3.2.24 on 2024-02-20 16:23

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0023_alter_roomsmodel_expires'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 16, 38, 42, 146501, tzinfo=utc)),
        ),
    ]
