from django.core.exceptions import ObjectDoesNotExist
import json
from asgiref.sync import sync_to_async
from game.models import RoomsModel, PlayerRoomModel, PlayersModel

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q

from .data import pong_data
import random
import time
# @sync_to_async
# def get_room_by_id(roomId):
#     return RoomsModel.objects.filter(id=roomId).first()

@sync_to_async
def set_power_play(consumer):
    if consumer.room.power:
        consumer.room.power = False
    else:
        consumer.room.power = True
    consumer.room.save()

@sync_to_async
def set_ai_player(consumer):
    if consumer.room.ai_player:
        consumer.room.ai_player = False
    else:
        consumer.room.ai_player = True
    consumer.room.save()

@sync_to_async
def get_info(consumer):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
        consumer.player = PlayerRoomModel.objects.get(room=consumer.room_id, id=consumer.player_id)
        consumer.server = PlayerRoomModel.objects.get(room=consumer.room_id, player=consumer.room.server)
        consumer.room.dy = random.choice([1, -1])
        # consumer.room.ddy = random.choice(consumer.choices)
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
def get_room_data(consumer):
    try:
        players = PlayerRoomModel.objects.filter(room=consumer.room_id)
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
        return json.dumps({
            'ai_player': consumer.room.ai_player,
            'power_play': consumer.room.power,
            'ball': {'x': consumer.room.x, 'y':consumer.room.y},
            'players': [{'x': i.x, 'y': i.y} for i in players]
        })
    except ObjectDoesNotExist:
        print(f"Room with ID {consumer.room.id} does not exist.")
        return None
    except MultipleObjectsReturned:
        print(f"More than one room with ID {consumer.room.id}.")
        return None

@sync_to_async
def get_teams_data(consumer, room_id):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    except RoomsModel.DoesNotExist:
        print(f"Room with ID {room_id} does not exist.")
        return None
    try:
        consumer.player = PlayerRoomModel.objects.get(room=room_id, id=consumer.player_id)
        consumer.server = PlayerRoomModel.objects.get(room=room_id, player=consumer.room.server)
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
    players = PlayerRoomModel.objects.filter(room=room.id)
    winner = ''
    winning_score = 0
    if room.score0 > room.score1:
        winner = 'player0'
        winning_score = room.score0
        print(players.get(side=0))
        print(players.get(side=1))
        players.get(side=0).player.history += 'W'
        players.get(side=1).player.history += 'L'
        players.get(side=0).player.score_history += str(room.score0) + '-' + str(room.score1)
        players.get(side=1).player.score_history += str(room.score0) + '-' + str(room.score1)
        players.get(side=0).player.date_history += room.expires
        players.get(side=1).player.date_history += room.expires
        players.get(side=0).save()
        players.get(side=1).save()
    elif room.score1 > room.score0:
        winner = 'player1'
        winning_score = room.score1
        print(players.get(side=0))
        print(players.get(side=1))
        players.get(side=0).player.history += 'L'
        players.get(side=1).player.history += 'W'
        players.get(side=0).player.score_history += str(room.score0) + '-' + str(room.score1)
        players.get(side=1).player.score_history += str(room.score0) + '-' + str(room.score1)
        players.get(side=0).player.date_history += room.expires
        players.get(side=1).player.date_history += room.expires
        players.get(side=0).save()
        players.get(side=1).save()
    print('on entre la dedans ?')
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
        consumer.server = PlayerRoomModel.objects.get(room=consumer.room_id, player=consumer.room.server)
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False
    consumer.room.started = True
    consumer.room.save()
    return True

@sync_to_async
def end_game(consumer):
    # print(f"Ending game in room {consumer.room_id}.")
    if consumer.room.x <= 0:
        consumer.room.score1 += 1
    else:
        consumer.room.score0 += 1
    consumer.room.started = False
    consumer.room.save()
    change_server(consumer)

@sync_to_async
def quit(consumer):
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 0:
        return
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 1:
        consumer.room.delete()
        return
    if PlayerRoomModel.objects.filter(room=consumer.room_id).count() == 2 and consumer.room.ai_player:
        consumer.room.ai_player = False
        consumer.room.save()
        try:
            player = PlayersModel.objects.get(login='ai')
        except PlayersModel.DoesNotExist:
            print("Error: AI player not found.")
        PlayerRoomModel.objects.get(room=consumer.room.id, player=player.id).delete()
        time.sleep(1.01)
        consumer.room.delete()
        return
    if consumer.player == None:
        return
    if consumer.server == consumer.player:
        consumer.player.delete()
        change_server(consumer)
    else:
        consumer.player.delete()

@sync_to_async
def remove_player(consumer):
    if consumer.player is not None:
        consumer.player.delete()


@sync_to_async
def check_player(consumer):
    try:
        consumer.player = PlayerRoomModel.objects.get(room=consumer.room_id, id=consumer.player_id)
    except ObjectDoesNotExist:
        return False
    if (consumer.player == None):
        return False
    return True

@sync_to_async
def change_side(consumer):
    if consumer.player.side == 0:
        consumer.player.side = 1
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.server = PlayerRoomModel.objects.get(room=consumer.room_id, player=consumer.room.server)
            consumer.room.x = consumer.server.x - pong_data['RADIUS']
            consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
            consumer.room.dx = -1
            consumer.room.dy = random.choice([1, -1])
            consumer.room.save()
    else:
        consumer.player.side = 0
        consumer.player.x = pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.server = PlayerRoomModel.objects.get(room=consumer.room_id, player=consumer.room.server)
            consumer.room.x = consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
            consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
            consumer.room.dx = 1
            consumer.room.dy = random.choice([1, -1])
            consumer.room.save()

@sync_to_async
def change_server_async(consumer):
    change_server(consumer)

def change_server(consumer):
    print(f"Changing server in room {consumer.room_id}.")
    if (PlayerRoomModel.objects.filter(room=consumer.room_id).count() > 1):
        condition = ~Q(id=consumer.server.id)
        consumer.server = PlayerRoomModel.objects.get(condition, room=consumer.room_id)
    else:
        consumer.server = PlayerRoomModel.objects.filter(room=consumer.room_id).first()
    consumer.room.server = consumer.server.player
    if consumer.server.side == 0:
        consumer.room.x = consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
        consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.room.dx = 1
        consumer.room.dy = random.choice([1, -1])
    else:
        consumer.room.x = consumer.server.x - pong_data['RADIUS']
        consumer.room.y = consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2
        consumer.room.dx = -1
        consumer.room.dy = random.choice([1, -1])
    consumer.room.save()
