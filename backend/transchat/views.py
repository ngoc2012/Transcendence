from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Message

@csrf_exempt
def chat_index(request):
	if request.method == 'POST':
		if 'username' in request.POST:
			username = request.POST['username']
		else:
			username = 'username'

		if 'room' in request.POST:
			room = request.POST['room']
		else:
			room = 'default'

		print(username)
		print(room)

		try:
			get_room = Room.objects.get(room_name=room)
			return redirect('room', room_name=room, username=username)
		
		except Room.DoesNotExist:
			new_room = Room(room_name=room)
			new_room.save()
			return redirect('room', room_name=room, username=username)

	return render(request, 'chat.html')

@csrf_exempt
def room(request, room_name, username):
	get_room = Room.objects.get(room_name=room_name)

	if request.method == 'POST':
		message =request.POST['message']
		print(message)
		new_message = Message(room=get_room, sender=username, message=message)
		new_message.save()

	get_messages = Message.objects.filter(room=get_room)
	context={
		"messages": get_messages,
		"user": username
	}
	return render(request, 'message.html', context)