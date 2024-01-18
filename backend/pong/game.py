from django.core.exceptions import ObjectDoesNotExist
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayerRoomModel, PlayersModel

import asyncio

from .data import pong_data
import random

@sync_to_async
def get_info(consumer):
    consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    consumer.player = PlayerRoomModel.objects.get(id=consumer.player_id)
    consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)

@sync_to_async
def get_room_data(players, room_id):
    try:
        room = RoomsModel.objects.get(id=room_id)
        return json.dumps({
            'ball': {'x': room.x, 'y':room.y},
            'players': [{'x': i.x, 'y': i.y} for i in players]
        })
    except ObjectDoesNotExist:
        return "Error: Rooms not found"

@sync_to_async
def get_teams_data(room_id):
    players0 = PlayerRoomModel.objects.filter(room=room_id, side=0)
    players1 = PlayerRoomModel.objects.filter(room=room_id, side=1)
    return json.dumps({
        'team0': [i.player.name for i in players0],
        'team1': [i.player.name for i in players1]
        })

@sync_to_async
def get_score_data(room_id):
    room = RoomsModel.objects.get(id=room_id)
    return json.dumps({ 'score': [room.score0, room.score1] })

@sync_to_async
def start_game(consumer):
    consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
    consumer.room.started = True
    consumer.room.save()

@sync_to_async
def end_game(consumer):
    consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
    if consumer.room.x <= 0:
        consumer.room.score1 += 1
    else:
        consumer.room.score0 += 1
    consumer.room.x = consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
    consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
    consumer.room.started = False
    consumer.room.save()

@sync_to_async
def quit(consumer):
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 1:
        consumer.room.delete()
    if consumer.server == consumer.player:
        consumer.player.delete()
        change_server(consumer, PlayerRoomModel.objects.filter(room=consumer.room_id).first())
    else:
        print("Player deleted")
        consumer.player.delete()

@sync_to_async
def change_side(consumer):
    if consumer.player.side == 0:
        consumer.player.side = 1
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
    else:
        consumer.player.side = 0
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
    consumer.player.save()

def change_server(consumer, player):
    consumer.server = player
    #consumer.room.server = PlayersModel.objects.get(player=consumer.room.server)
    #consumer.room.save()
