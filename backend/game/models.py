import uuid
from django.db import models
from django.utils import timezone

class PlayersModel(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    #session_id = models.CharField(max_length=40)
    #expires = models.DateTimeField()
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class RoomsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    game = models.CharField(max_length=20)
    nplayers = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(PlayersModel, on_delete=models.CASCADE)
    expires = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=15))
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.id)
    def check_expired(self):
        if self.expires and self.expires < timezone.now():
            self.delete()

class PlayerRoomModel(models.Model):
    player = models.ForeignKey(PlayersModel, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomsModel, on_delete=models.CASCADE)
