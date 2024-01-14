# Generated by Django 3.2.12 on 2024-01-14 11:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20240114_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 14, 11, 25, 11, 864000, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='roomsmodel',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
