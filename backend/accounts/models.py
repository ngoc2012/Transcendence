from django.contrib.auth.models import AbstractUser
from django.db import models


class PlayersModel(AbstractUser):
    login = models.CharField(default='', max_length=255, unique=True)
    name = models.CharField(max_length=255)
    secret_2fa = models.TextField(default='', blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    elo = models.IntegerField(default=1500)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        self.login = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username