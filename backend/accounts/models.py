from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class PlayersModel(AbstractUser):
    id = models.AutoField(primary_key=True)
    login = models.CharField(default='', max_length=255, unique=True)
    name = models.CharField(max_length=255)
    secret_2fa = models.TextField(default='', blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    elo = models.IntegerField(default=1500)
    history = models.CharField(max_length=10)
    score_history = models.CharField(max_length=70)
    online_status = models.CharField(max_length=8, default='Offline')
    tourn_alias = models.CharField(max_length=255)
    friends = models.ManyToManyField("self", blank=True)
    acc = models.CharField(max_length=255)
    ref = models.CharField(max_length=255)
    ws_token = models.CharField(max_length=255, blank=True, null=True)
    ws_token_expires = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['username']

    def generate_ws_token(self):
        import uuid
        from django.utils import timezone

        self.ws_token = str(uuid.uuid4())
        self.ws_token_expires = timezone.now() + datetime.timedelta(minutes=5)
        self.save()
        return self.ws_token

    def validate_ws_token(self, token):
        from django.utils import timezone

        if self.ws_token == token and timezone.now() < self.ws_token_expires:
            self.ws_token = None
            self.ws_token_expires = None
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        self.login = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username