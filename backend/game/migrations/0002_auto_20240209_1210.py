# Generated by Django 3.2.24 on 2024-02-09 12:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playersmodel',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='playersmodel',
            name='secret_2fa',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 9, 12, 25, 8, 876739, tzinfo=utc)),
        ),
    ]
