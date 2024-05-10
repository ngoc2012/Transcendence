from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room, User
from accounts.models import PlayersModel
from accounts.forms import ChatMessageForm
from django.views.decorators.csrf import csrf_exempt, csrf_protect

@csrf_protect
def lobby(request):
    if request.method == 'GET':
        if 'username' in request.GET:
            username = request.GET['username']
            try:
                get_user = PlayersModel.objects.filter(login=username).get()
                request.session['user'] = username
                return render(request, 'chat_signup.html', {"username": username})
            except PlayersModel.DoesNotExist:
                response = HttpResponse("You must be logged in")
                response.status_code = 401
                return render(request, 'chat_signup.html', {"username": username})
    if request.method == 'POST':
        try:
            Room.objects.get(room_name='general_chat')
        except Room.DoesNotExist:
            room = Room(room_name='general_chat')
            room.save()
        if 'username' in request.POST:
            username = request.POST['username']
            request.session['user'] = username
            return HttpResponse("User ready to chat")

@csrf_protect
def chatroom(request, room_name):
    try:
        room = Room.objects.get(room_name=room_name)
    except Room.DoesNotExist:
        new_room = Room(room_name=room_name)
        new_room.save()
    user = PlayersModel.objects.get(login=request.session['user'])
    try:
        room = Room.objects.get(room_name=room_name)
        room.users.add(user)
        room.save()
        return render(request, "chatroom.html")
    except Room.DoesNotExist:
        new_room = Room(room_name=room_name)
        new_room.users.add(user)
        new_room.save()
        return render(request, "chatroom.html")
    
def verify(request):
    form = ChatMessageForm(type='chat_message', user=request.POST['user'], message=request.POST['message'])
    if form.is_valid():
        response = HttpResponse("Valid data")
        response.status_code = 200
        return response
    response = HttpResponse("Invalid data")
    response.status_code = 400
    return response
