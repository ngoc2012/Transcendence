from django.db import models

class User(models.Model):
	username = models.CharField(max_length=20)
	blocked_user = []

	def __str__(self):
		return self.username

class Room(models.Model):
	room_name = models.CharField(max_length=25)
	users = []

	def __str__(self):
		return self.room_name