from django.core.exceptions import ObjectDoesNotExist
import json
from asgiref.sync import sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayerRoomModel, PlayersModel

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .data import pong_data

@sync_to_async
def get_info(consumer):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
        print('consumer.room:')
        print(consumer.room)
        consumer.player = PlayerRoomModel.objects.get(id=consumer.player_id)
        print('consumer.player:')
        print(consumer.player)
        consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
        print('consumer.server:')
        print(consumer.server)
    except ObjectDoesNotExist:
        print(f"Room with ID {consumer.room_id} does not exist.")   
        return False
    except MultipleObjectsReturned:
        return False
    print(f"Player {consumer.player_id} connected to room {consumer.room_id}.", PlayerRoomModel.objects.filter(room=consumer.room_id).count())
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() < 2:
        return False
    return True

@sync_to_async
def get_room_data(players, room_id):
    try:
        room = RoomsModel.objects.get(id=room_id)
        return json.dumps({
            'ball': {'x': room.x, 'y':room.y},
            'players': [{'x': i.x, 'y': i.y} for i in players]
        })
    except ObjectDoesNotExist:
        print(f"Room with ID {room_id} does not exist.")
        return None
    except MultipleObjectsReturned:
        print(f"More than one room with ID {room_id}.")
        return None

@sync_to_async
def get_teams_data(consumer, room_id):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    except RoomsModel.DoesNotExist:
        print(f"Room with ID {room_id} does not exist.")
        return None
    try:
        consumer.player = PlayerRoomModel.objects.get(id=consumer.player_id)
        consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
        players0 = PlayerRoomModel.objects.filter(room=room_id, side=0)
        players1 = PlayerRoomModel.objects.filter(room=room_id, side=1)
    except MultipleObjectsReturned:
        return None
    return json.dumps({
        'team0': [i.player.name for i in players0],
        'team1': [i.player.name for i in players1]
        })

@sync_to_async
def get_score_data(room_id):
    room = RoomsModel.objects.get(id=room_id)
    return json.dumps({ 'score': [room.score0, room.score1] })

@sync_to_async
def get_win_data(room_id):
    room = RoomsModel.objects.get(id=room_id)
    winner = ''
    winning_score = 0
    if room.score0 > room.score1:
        winner = 'player0'
        winning_score = room.score0
    elif room.score1 > room.score0:
        winner = 'player1'
        winning_score = room.score1
    return json.dumps({
        'win': winner,
        'score': [room.score0, room.score1],
        'winning_score': winning_score,
        'roomid': room_id
    })

@sync_to_async
def start_game(consumer):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
        consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False
    consumer.room.started = True
    consumer.room.save()
    return True

@sync_to_async
def end_game(consumer):
    consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
    if consumer.room.x <= 0:
        consumer.room.score1 += 1
    else:
        consumer.room.score0 += 1
    if consumer.player.side == 0:
        consumer.room.x = consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
        consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.dx = 1
    else:
        consumer.room.x = consumer.server.x - pong_data['RADIUS']
        consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.dx = -1
    consumer.room.started = False
    consumer.room.save()

@sync_to_async
def quit(consumer):
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 0:
        return
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 1:
        consumer.room.delete()
        return
    if consumer.player == None:
        return
    if consumer.server == consumer.player:
        consumer.player.delete()
        change_server(consumer, PlayerRoomModel.objects.filter(room=consumer.room_id).first())
    else:
        consumer.player.delete()

@sync_to_async
def remove_player(consumer):
    if consumer.player is not None:
        consumer.player.delete()

@sync_to_async
def check_player(consumer):
    try:
        consumer.player = PlayerRoomModel.objects.get(id=consumer.player_id)
    except ObjectDoesNotExist:
        return False
    if (consumer.player == None):
        return False
    return True

@sync_to_async
def change_server_direction(consumer):
    print("change direction")
    consumer.dy *= -1

@sync_to_async
def change_side(consumer):
    if consumer.player.side == 0:
        consumer.player.side = 1
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
            consumer.room.x = consumer.server.x - pong_data['RADIUS']
            consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
            consumer.dx = -1
            consumer.room.save()
    else:
        consumer.player.side = 0
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)
            consumer.room.x = consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
            consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
            consumer.dx = 1
            consumer.room.save()

def change_server(consumer, player):
    consumer.server = player
    consumer.room.server = consumer.server.player
    if player.side == 0:
        consumer.room.x = player.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
        consumer.room.y = player.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.dx = 1
    else:
        consumer.room.x = player.x - pong_data['RADIUS']
        consumer.room.y = player.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.dx = -1
    consumer.room.save()
