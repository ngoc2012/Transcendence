# Generated by Django 3.2.12 on 2024-01-14 15:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20240114_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerroommodel',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='playerroommodel',
            name='side',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 14, 16, 7, 11, 671162, tzinfo=utc)),
        ),
    ]
