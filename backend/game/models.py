import uuid
from django.db import models
from django.utils import timezone

class PlayersModel(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    session_id = models.CharField(max_length=40, null=True)
    expires = models.DateTimeField(null=True)
    def __str__(self):
        return str(self.id)

class RoomsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    game = models.CharField(max_length=20)
    owner = models.ForeignKey(PlayersModel, on_delete=models.CASCADE, related_name='own')
    server = models.ForeignKey(PlayersModel, on_delete=models.CASCADE, related_name='serve', null=True)
    expires = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=15))
    started = models.BooleanField(default=False)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    score0 = models.IntegerField(default=0)
    score1 = models.IntegerField(default=0)
    def __str__(self):
        return str(self.id)
    def check_expired(self):
        if self.expires and self.expires < timezone.now():
            self.delete()

class PlayerRoomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(PlayersModel, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomsModel, on_delete=models.CASCADE)
    side = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.id)
