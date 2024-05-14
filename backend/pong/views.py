from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import RoomsModel
from accounts.models import PlayersModel
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .data import pong_data
from django.core.cache import cache

def index(request):
    return render(request, "pong.html")

def index_local(request):
    return render(request, "pong_local.html")

from backend.asgi import channel_layer
from asgiref.sync import async_to_sync
def action(request, room_id, player_id, action):
    k_x = room_id + "_x"
    k_y = room_id + "_y"
    k_player_x = room_id + "_" + player_id + "_x"
    k_player_y = room_id + "_" + player_id + "_y"
    player_id = int(player_id)
    started = cache.get(room_id + "_started")
    team0 = cache.get(room_id + "_team0")
    if team0 == None:
        team0 = []
    team1 = cache.get(room_id + "_team1")
    if team1 == None:
        team1 = []
    server = cache.get(room_id + "_server")
    x = cache.get(k_x)
    y = cache.get(k_y)
    player_x = cache.get(k_player_x)
    player_y = cache.get(k_player_y)
    if started == None:
        return HttpResponse("NULL")
    if action == 'state':
        return JsonResponse({
            'ai_player': cache.get(room_id + "_ai"),
            'power_play': cache.get(room_id + "_pow"),
            'ball': {'x': x, 'y':y},
            'team0': team0,
            'team1': team1,
            'dx': cache.get(room_id + "_dx"),
            'started': started,
            'server': player_id == server,
            'x': player_x,
            'y': player_y,
        })
    
    if action == 'up':
        if player_y > 0:
            cache.set(k_player_y, player_y - pong_data['STEP'])
            if not started and server == player_id:
                cache.set(k_y, y - pong_data['STEP'])
    elif action == 'down':
        if player_y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
            cache.set(k_player_y, player_y + pong_data['STEP'])
            if not started and server == player_id:
                cache.set(k_y, y + pong_data['STEP'])
    elif action == 'left':
        if (player_id in team0 and player_x > 0) \
            or (player_id in team1 and player_x > 3 * pong_data['WIDTH'] / 4):
            cache.set(k_player_x, player_x - pong_data['STEP_X'])
            if not started and server == player_id:
                cache.set(k_x, x - pong_data['STEP_X'])
    elif action == 'right':
        if (player_id in team0 and player_x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
            or (player_id in team1 and player_x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
            cache.set(k_player_x, player_x + pong_data['STEP_X'])
            if not started and server == player_id:
                cache.set(k_x, x + pong_data['STEP_X'])
    async_to_sync(channel_layer.group_send)(room_id, {'type': 'group_data'})
    x = cache.get(k_x)
    y = cache.get(k_y)
    player_x = cache.get(k_player_x)
    player_y = cache.get(k_player_y)
    return JsonResponse({
        'ai_player': cache.get(room_id + "_ai"),
        'power_play': cache.get(room_id + "_pow"),
        'ball': {'x': x, 'y':y},
        'team0': team0,
        'team1': team1,
        'dx': cache.get(room_id + "_dx"),
        'started': started,
        'x': player_x,
        'y': player_y,
    })

from backend.asgi import channel_layer
from asgiref.sync import async_to_sync
def close_connection(request, room_id, player_id):
    async_to_sync(channel_layer.group_send)(
        room_id,
        {
            'type': 'close_connection',
            'player_id': player_id
        }
    )
    return HttpResponse("done")

def start(request, room_id):
    async_to_sync(channel_layer.group_send)(
        room_id,
        {
            'type': 'start',
        }
    )
    return HttpResponse("done")