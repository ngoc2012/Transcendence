from django.db import models

class Room(models.Model):
	room_name = models.CharField(max_length=25)

	def __str__(self):
		return self.room_name
	
class Message(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	sender = models.CharField(max_length=25)
	message = models.TextField()

	def __str__(self):
		return self.room