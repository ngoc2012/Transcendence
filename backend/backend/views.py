from django.shortcuts import render
from django.http import HttpResponse

rooms = {}
online_players = {}

def lobby(request):
	return (render(request, 'lobby.html'))

def new_player(request):
    i = 0
    user_name = "user" + str(i)
    while (user_name in online_players.keys()):
        i += 1
        user_name = "user" + str(i)
    return (HttpResponse(user_name))

def new_room(request):
    global rooms

    # Get the channel layer
    channel_layer = get_channel_layer()

    i = 0
    while (i in rooms):
        i += 1
    return (HttpResponse(str(i)))

