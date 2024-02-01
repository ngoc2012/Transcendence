# Generated by Django 4.2.9 on 2024-02-01 13:47

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlayersModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('login', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('session_id', models.CharField(max_length=40, null=True)),
                ('expires', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoomsModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('game', models.CharField(max_length=20)),
                ('expires', models.DateTimeField(default=datetime.datetime(2024, 2, 1, 14, 2, 26, 202441, tzinfo=datetime.timezone.utc))),
                ('started', models.BooleanField(default=False)),
                ('x', models.IntegerField(blank=True, null=True)),
                ('y', models.IntegerField(blank=True, null=True)),
                ('score0', models.IntegerField(default=0)),
                ('score1', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='own', to='game.playersmodel')),
                ('server', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='serve', to='game.playersmodel')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerRoomModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('side', models.IntegerField(blank=True, null=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('x', models.IntegerField(blank=True, null=True)),
                ('y', models.IntegerField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.playersmodel')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.roomsmodel')),
            ],
        ),
    ]
