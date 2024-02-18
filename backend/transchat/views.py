from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Message, User

@csrf_exempt
def lobby(request):
    return render(request, 'chat_signup.html')

@csrf_exempt
def chatroom(request, room_name):
    return render(request, "chatroom.html", {"room_name": room_name})