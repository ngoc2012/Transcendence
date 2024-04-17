from django.db import models

class User(models.Model):
	username = models.CharField(max_length=20)
	blocked_user = models.ManyToManyField("self", blank=True, symmetrical=False)
	
	def __str__(self):
		return self.username

class Room(models.Model):
	room_name = models.CharField(max_length=25)
	users = models.ManyToManyField(User, blank=True)

	def __str__(self):
		return self.room_name