from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    pass
    name = models.CharField(max_length=255)
    secret_2fa = models.TextField(default='', blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    elo = models.IntegerField(default=1500)

    def __str__(self):
        return self.username

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