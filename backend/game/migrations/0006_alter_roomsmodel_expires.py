# Generated by Django 5.0.2 on 2024-02-14 11:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_alter_roomsmodel_expires'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 11, 53, 48, 467520, tzinfo=datetime.timezone.utc)),
        ),
    ]
