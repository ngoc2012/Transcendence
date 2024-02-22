from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room, User

@csrf_exempt
def lobby(request):
    if request.method == 'GET':
        if 'username' in request.GET:
            username = request.GET['username']
            try:
                get_user = User.objects.filter(username=username).get()
                request.session['user'] = username
                return render(request, 'chat_signup.html', {"username": username})
            except User.DoesNotExist:
                new_user = User(username=username)
                new_user.save()
                request.session['user'] = username
                return render(request, 'chat_signup.html', {"username": username})
    if request.method == 'POST':
        if 'username' in request.POST:
            username = request.POST['username']
    return render(request, 'chat_signup.html', {"username": username})

@csrf_exempt
def chatroom(request, room_name):
    user = User.objects.get(username=request.session['user'])
    try:
        room = Room.objects.get(room_name=room_name)
    except Room.DoesNotExist:
        new_room = Room(room_name=room_name)
        new_room.save()
        return render(request, "chatroom.html", {"room_name": room_name, "user":user})
    return render(request, "chatroom.html", {"room_name": room_name, "user":user})