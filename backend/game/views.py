import requests  # Add this line

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RoomsModel, PlayersModel, PlayerRoomModel

from pong.data import pong_data

def get_data(game):
    if game == 'pong':
        return pong_data
    return {}

@csrf_exempt
def new_game(request):
    if 'game' not in request.POST:
        return (HttpResponse("Error: No game!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'name' not in request.POST:
        return (HttpResponse("Error: No name!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    owner = PlayersModel.objects.get(login=request.POST['login'])
    new_room = RoomsModel(
        game=request.POST['game'],
        name=request.POST['name'],
        owner=owner,
        server=owner
    )
    if new_room.game == 'pong':
        new_room.x = pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
        new_room.y = pong_data['HEIGHT'] / 2
    new_room.save()
    player_room = PlayerRoomModel(
        player=owner,
        room=new_room,
        side=0,
        position=0
    )
    if new_room.game == 'pong':
        player_room.x = 0
        player_room.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
    player_room.save()
    return (JsonResponse({
        'id': str(new_room),
        'game': new_room.game,
        'name': new_room.name,
        'player_id': str(player_room),
        'data': get_data(new_room.game)
        }))

@csrf_exempt
def join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login " + request.POST['login'] + " does not exist!"))
    #uuid_obj = UUID(uuid_str)
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    room = RoomsModel.objects.get(id=request.POST['game_id'])
    n0 = PlayerRoomModel.objects.filter(room=room, side=0).count()
    n1 = PlayerRoomModel.objects.filter(room=room, side=1).count()
    if n1 > n0:
        side = 0
        position = n0
    else:
        side = 1
        position = n1
    player = PlayersModel.objects.get(login=request.POST['login'])
    player_room = PlayerRoomModel(
        player=player,
        room=room,
        side=side,
        position=position
    )
    if room.game == 'pong':
        player_room.x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
        if side == 1:
            player_room.x = pong_data['WIDTH'] - player_room.x - pong_data['PADDLE_WIDTH']
        player_room.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
    player_room.save()
    player.save()
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': str(player_room),
        'data': get_data(room.game)
        }))

@csrf_exempt
def delete(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    owner = PlayersModel.objects.get(login=request.POST['login'])
    #uuid_obj = UUID(uuid_str)
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id '" + request.POST['game_id'] + "' does not exist!"))
    room = RoomsModel.objects.get(id=request.POST['game_id'])
    s = "Room " + room.name + ' - ' + str(room) + " deleted"
    room.delete()
    if room.owner == owner:
        return (HttpResponse(s))
    return (HttpResponse("Error: Login '" + request.POST['login'] + "' is not the owner of '" + request.POST['game_id'] + "'!"))

