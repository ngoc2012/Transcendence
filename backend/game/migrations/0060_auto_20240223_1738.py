# Generated by Django 3.2.24 on 2024-02-23 17:38

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0059_alter_roomsmodel_expires'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentmatchmodel',
            name='status',
            field=models.CharField(default='Waiting for players to join', max_length=255),
        ),
        migrations.AlterField(
            model_name='roomsmodel',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 23, 17, 53, 22, 141738, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='TournamentRoomsModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('game', models.CharField(max_length=20)),
                ('expires', models.DateTimeField(default=datetime.datetime(2024, 2, 23, 17, 53, 22, 143697, tzinfo=utc))),
                ('started', models.BooleanField(default=False)),
                ('x', models.IntegerField(blank=True, null=True)),
                ('y', models.IntegerField(blank=True, null=True)),
                ('score0', models.IntegerField(default=0)),
                ('score1', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownTour', to='game.playersmodel')),
                ('server', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='serveTour', to='game.playersmodel')),
            ],
        ),
        migrations.AlterField(
            model_name='tournamentmatchmodel',
            name='room',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_result', to='game.tournamentroomsmodel'),
        ),
    ]
