from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from game.models import RoomsModel, PlayerRoomModel
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .data import pong_data
from django.core.cache import cache

def index(request):
    return render(request, "pong.html")

from backend.asgi import channel_layer
from asgiref.sync import async_to_sync
def action(request, room_id, player_id, action):
    try:
        room = RoomsModel.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return HttpResponse("NULL")
    if action == 'state':
        try:
            players = PlayerRoomModel.objects.filter(room=room_id)
        except ObjectDoesNotExist:
            return HttpResponse("error")
        return JsonResponse({
            'ai_player': cache.get(room_id + "_ai"),
            'power_play': cache.get(room_id + "_pow"),
            'ball': {'x': cache.get(room_id + "_x"), 'y':cache.get(room_id + "_y")},
            'side': {i.player.login: i.side for i in players},
            'dx': cache.get(room_id + "_dx"),
            'started': room.started,
            'x': {i.player.login: cache.get(room_id + "_" + str(i.id) + "_x") for i in players},
            'y': {i.player.login: cache.get(room_id + "_" + str(i.id) + "_y") for i in players},
            'players': [{'x': cache.get(room_id + "_" + str(i.id) + "_x"),
                         'y': cache.get(room_id + "_" + str(i.id) + "_y")} for i in players]
        })
    try:
        player, server =    PlayerRoomModel.objects.get(room=room_id, player=player_id), \
                            PlayerRoomModel.objects.get(room=room_id, player=room.server)
    except MultipleObjectsReturned:
        return HttpResponse("error")
    except ObjectDoesNotExist:
        return HttpResponse("error")
    if action == 'up':
        k_player_y = room_id + "_" + str(player.id) + "_y"
        y = cache.get(k_player_y)
        if y > 0:
            cache.set(k_player_y, y - pong_data['STEP'])
            if not room.started and server == player:
                cache.set(room_id + "_y", cache.get(room_id + "_y") - pong_data['STEP'])
    elif action == 'down':
        k_player_y = room_id + "_" + str(player.id) + "_y"
        y = cache.get(k_player_y)
        if y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
            cache.set(k_player_y, y + pong_data['STEP'])
            if not room.started and server == player:
                cache.set(room_id + "_y", cache.get(room_id + "_y") + pong_data['STEP'])
    elif action == 'left':
        k_player_x = room_id + "_" + str(player.id) + "_x"
        x = cache.get(k_player_x)
        if (player.side == 0 and x > 0) \
            or (player.side == 1 and x > 3 * pong_data['WIDTH'] / 4):
            cache.set(k_player_x, x - pong_data['STEP_X'])
            if not room.started and server == player:
                cache.set(room_id + "_x", cache.get(room_id + "_x") - pong_data['STEP_X'])
    elif action == 'right':
        k_player_x = room_id + "_" + str(player.id) + "_x"
        x = cache.get(k_player_x)
        if (player.side == 0 and x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
            or (player.side == 1 and x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
            cache.set(k_player_x, x + pong_data['STEP_X'])
            if not room.started and server == player:
                cache.set(room_id + "_x", cache.get(room_id + "_x") + pong_data['STEP_X'])
    async_to_sync(channel_layer.group_send)(room_id, {'type': 'group_data'})
    return HttpResponse("done")

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