from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Room

@csrf_exempt
def chat_index(request):
	if request.method == 'POST':
		print("on entre")
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
	print("on est dans room")
	print(room_name)
	print(username)
	return render(request, 'message.html')