from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import RoomsModel, PlayersModel, PlayerRoomModel

from pong.data import pong_data

# Create your views here.
def index(request):
    return render(request, "pong.html")

@csrf_exempt
def state(request):
    if 'action' not in request.POST:
        return (HttpResponse("Error: No action!"))
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST or request.POST['login'] == "":
        return (HttpResponse("Error: No login!"))
    player = PlayersModel.objects.get(login=request.POST['login'])
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id '" + request.POST['game_id'] + "' does not exist!"))
    room = RoomsModel.objects.get(id=request.POST['game_id'])
    if not PlayerRoomModel.objects.filter(player=player,room=room).exists():
        return (HttpResponse("Error: Player is not playing this game!"))
    player_room = PlayerRoomModel.objects.get(player=player,room=room)
    if room.game == 'pong':
        #print(request.POST['action'])
        if request.POST['action'] == 'down' and player_room.y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
            player_room.y += pong_data['STEP']
            player_room.save()
            if room.server == player:
                room.y += pong_data['STEP']
                room.save()
        if request.POST['action'] == 'up' and player_room.y > 0:
            player_room.y -= pong_data['STEP']
            player_room.save()
            if room.server == player:
                room.y -= pong_data['STEP']
                room.save()
    return (HttpResponse("Done"))
