from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .models import RoomsModel, TournamentMatchModel, TournamentModel
from accounts.models import PlayersModel
from pong.data import pong_data
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils import timezone

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

User = get_user_model()

def get_data(game):
    if game == 'pong':
        return pong_data
    return {}

def add_player_to_room(game_id, login):
    if not RoomsModel.objects.filter(id=game_id).exists():
        return None, None
    room = RoomsModel.objects.get(id=game_id)

    if not PlayersModel.objects.filter(login=login).exists():
        return room, None
    player = PlayersModel.objects.get(login=login)

    k_team0 = str(room.id) + "_team0"
    k_team1 = str(room.id) + "_team1"
    k_players = str(room.id) + "_all"
    team0 = cache.get(k_team0)
    if team0 == None:
        team0 = []
    team1 = cache.get(k_team1)
    if team1 == None:
        team1 = []
    players = cache.get(k_players)
    if players == None:
        players = []
    n0 = len(team0)
    n1 = len(team1)
    if n1 >= n0:
        team0.append(player.id)
        cache.set(k_team0, team0)
        position = n0
    else:
        team1.append(player.id)
        cache.set(k_team1, team1)
        position = n1
    players.append(player.id)
    cache.set(k_players, players)
    if room.game == 'pong':
        k_player_x = str(room.id) + "_" + str(player.id) + "_x"
        k_player_y = str(room.id) + "_" + str(player.id) + "_y"
        player_x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
        cache.set(k_player_x, player_x)
        if player.id not in team0:
            cache.set(k_player_x, pong_data['WIDTH'] - player_x - pong_data['PADDLE_WIDTH'])
        cache.set(k_player_y, pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2)
    return room, player


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
    room = RoomsModel(
        game=request.POST['game'],
        name=request.POST['name'],
        owner=request.user,
    )
    room.player0 = PlayersModel.objects.get(login=request.POST['login'])
    room.save()
    if room.game == 'pong':
        cache.set(str(room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(str(room.id) + "_y", pong_data['HEIGHT'] / 2)
        room, player = add_player_to_room(room.id, request.POST['login'])
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))


@csrf_exempt
def update(request):
    data = {
        "rooms": [
            {
                "id": str(room.id),
                "name": room.name,
                "owner": room.player0.login,
            } for room in RoomsModel.objects.filter(tournamentRoom=False)
        ]
    }
    return JsonResponse(data, safe=False)

@csrf_exempt
def join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    players = cache.get(str(request.POST['game_id']) + "_all")
    if players == None:
        players = []
    player_login = request.POST['login']
    room_id = request.POST['game_id']
    try:
        player = PlayersModel.objects.get(login=player_login)
    except ObjectDoesNotExist:
        return (HttpResponse(f"Error: Player {player_login} does not exist."))
    except MultipleObjectsReturned:
        return (HttpResponse(f"Error: Many players with ID {player_login} exist."))
    try:
        room = RoomsModel.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return (HttpResponse(f"Error: Room with ID {room_id} does not exist."))
    except MultipleObjectsReturned:
        return (HttpResponse(f"Error: Many rooms with ID {room_id} exist."))
    room.player1 = player
    room.save()
    if player.id in players:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " is already in the room!"))
    room, player = add_player_to_room(request.POST['game_id'], request.POST['login'])
    if room == None:
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    if player == None:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " does not exist!"))
    return (JsonResponse({
            'id': str(room),
            'game': room.game,
            'name': room.name,
            'player_id': player.id,
            'data': get_data(room.game)
        }))

from backend.asgi import channel_layer
from asgiref.sync import async_to_sync

@csrf_exempt
def close_connection(request, login_id):
    async_to_sync(channel_layer.group_send)(
        "rooms",
        {
            'type': 'close_connection',
            'login_id': login_id
        }
    )
    return HttpResponse("done")

@csrf_exempt
def need_update(request):
    async_to_sync(channel_layer.group_send)(
        "rooms",
        {
            'type': 'group_room_list',
        }
    )
    return HttpResponse("done")
