from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Message, User



@csrf_exempt
def chat_lobby(request):
	if request.method == 'GET':
		if 'username' in request.GET:
			username = request.GET['username']
			try:
				get_user = User.objects.get(username=username)
				return redirect('signup', username=username)

			except User.DoesNotExist:
				new_user = User(username=username)
				new_user.save()
			return redirect('signup', username=username)
	return render(request, 'chat.html')

@csrf_exempt
def chat_signup(request, username):
	all_rooms = Room.objects.all()
	if 'room' in request.POST:
		room = request.POST['room']
		print("room = " + request.POST['room'])

		try:
			get_room = Room.objects.get(room_name=room)
			get_user = User.objects.get(username=username)
			get_user.rooms.add(get_room)
			request.session['username'] = get_user.username
			print("redirect room exist")
			return redirect('room', room_name=room)
		
		except Room.DoesNotExist:
			new_room = Room(room_name=room)
			get_user = User.objects.get(username=username)
			new_room.save()
			get_user.rooms.add(new_room)
			request.session['username'] = get_user.username
			print("redirect room does not exist")
			return redirect('room', room_name=room)
	return render(request, 'chat.html', {"username":username, "all_rooms":all_rooms})

@csrf_exempt
def room(request, room_name):
	print("room name = " + room_name)
	get_room = Room.objects.get(room_name=room_name)
	username = request.session['username']

	if request.method == 'POST':
		if 'message' in request.POST:
			message =request.POST['message']
			new_message = Message(room=get_room, sender=username, message=message)
			new_message.save()

	get_messages = Message.objects.filter(room=get_room)
	context={
		"messages": get_messages,
		"user": username
	}
	return render(request, 'message.html', context)