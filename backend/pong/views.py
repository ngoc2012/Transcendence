from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from game.models import RoomsModel, PlayerRoomModel
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .data import pong_data
# import json
# import os

# from django.conf import settings

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
            'ai_player': room.ai_player,
            'power_play': room.power,
            'ball': {'x': room.x, 'y':room.y},
            'side': {i.player.login: i.side for i in players},
            'dx': room.dx,
            'started': room.started,
            'x': {i.player.login: i.x for i in players},
            'y': {i.player.login: i.y for i in players},
            'players': [{'x': i.x, 'y': i.y} for i in players]
        })
    try:
        player, server = PlayerRoomModel.objects.get(player=player_id), PlayerRoomModel.objects.get(player=room.server)
    except MultipleObjectsReturned:
        return HttpResponse("error")
    except ObjectDoesNotExist:
        return HttpResponse("error")
    if action == 'up':
        if player.y > 0:
            player.y -= pong_data['STEP']
            player.save()
            if not room.started and server == player:
                room = RoomsModel.objects.get(id=room_id)
                room.y -= pong_data['STEP']
                room.save()
    elif action == 'down':
        if player.y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
            player.y += pong_data['STEP']
            player.save()
            if not room.started and server == player:
                room = RoomsModel.objects.get(id=room_id)
                room.y += pong_data['STEP']
                room.save()
    elif action == 'left':
        if  (player.side == 0 and player.x > 0) \
            or (player.side == 1 and player.x > 3 * pong_data['WIDTH'] / 4):
            player.x -= pong_data['STEP_X']
            player.save()
            if not room.started and server == player:
                room = RoomsModel.objects.get(id=room_id)
                room.x -= pong_data['STEP']
                room.save()
    elif action == 'right':
        if (player.side == 0 and player.x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
            or (player.side == 1 and player.x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
            player.x += pong_data['STEP_X']
            player.save()
            if not room.started and server == player:
                room = RoomsModel.objects.get(id=room_id)
                room.x += pong_data['STEP']
                room.save()
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