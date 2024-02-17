from django.db import models

class User(models.Model):
	username = models.CharField(max_length=20)
	blocked_user = models.ManyToManyField("self")

	def __str__(self):
		return self.username

class Room(models.Model):
	room_name = models.CharField(max_length=25)
	users = models.ManyToManyField(User)

	def __str__(self):
		return self.room_name
	
class Message(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	sender = models.CharField(max_length=25)
	message = models.TextField()

	def __str__(self):
		return str(self.room)
	
