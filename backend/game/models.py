import uuid
from django.db import models
from django.utils import timezone
from accounts.models import PlayersModel
from django.conf import settings

# class PlayersModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     login = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     secret_2fa = models.TextField(default='', blank=True)
#     email = models.EmailField(default='', blank=True)  # gerer si mauvais email
#     session_id = models.CharField(max_length=40, null=True, blank=True)
#     expires = models.DateTimeField(null=True, blank=True)
#     elo = models.IntegerField(default=1500)
#     def __str__(self):
#         return str(self.id)

class RoomsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    game = models.CharField(max_length=20)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='own')
    server = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='serve', null=True)
    expires = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=15))
    started = models.BooleanField(default=False)
    power = models.BooleanField(default=False)
    ai_player = models.BooleanField(default=False)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    dx = models.IntegerField(default=1)
    dy = models.IntegerField(default=1)
    # ddy = models.IntegerField(blank=True, null=True)
    score0 = models.IntegerField(default=0)
    score1 = models.IntegerField(default=0)
    tournamentRoom = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)
    def check_expired(self):
        if self.expires and self.expires < timezone.now():
            self.delete()   

class PlayerRoomModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomsModel, on_delete=models.CASCADE)
    side = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.id)
    
# Tournament classes

class TournamentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=False)
    game = models.CharField(max_length=20)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_tournament')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participating')
    waitlist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='waitlisted')
    eliminated = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='eliminated')
    round = models.IntegerField(default=1)
    active_matches = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    final = models.BooleanField(default=False)
    terminated = models.BooleanField(default=False)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='won_tournament', null=True, blank=True)
    local = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class TournamentMatchModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name='tournament')
    room = models.OneToOneField(RoomsModel, on_delete=models.SET_NULL, null=True, related_name='tournament_room')
    room_uuid = models.UUIDField(null=True, editable=False)
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tournament_player1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tournament_player2')
    p1_score = models.IntegerField(default=0)
    p2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_match_results')
    round_number = models.IntegerField(null=True, blank=True, help_text="The tournament round for this match")
    match_number = models.IntegerField(null=True, blank=True, help_text="The tournament match number")
    status = models.CharField(max_length=255, default='Waiting for players to join')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.tournament.name} : {self.player1.name} vs {self.player2.name} - Winner: {self.winner.name if self.winner else 'TBD'}"
