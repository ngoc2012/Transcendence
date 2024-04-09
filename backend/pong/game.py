from django.core.exceptions import ObjectDoesNotExist
import json
from asgiref.sync import sync_to_async
from game.models import RoomsModel, PlayerRoomModel, PlayersModel

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q

from .data import pong_data
import random
import time
from django.core.cache import cache

@sync_to_async
def set_power_play(consumer):
    if cache.get(consumer.k_pow):
        cache.set(consumer.k_pow, False)
    else:
        cache.set(consumer.k_pow, True)

@sync_to_async
def game_init(consumer):
    if cache.get(consumer.k_all) == None:
        print("Game init")
        cache.set(consumer.k_team0, [consumer.player.id])
        cache.set(consumer.k_team1, [])
        cache.set(consumer.k_all, [consumer.player.id])
        cache.set(consumer.k_server, consumer.player.id)
        cache.set(consumer.k_started, False)
        cache.set(consumer.k_dx, 1)
        cache.set(consumer.k_ddy, random.choice(consumer.choices))
        cache.set(consumer.k_dy, random.choice([1, -1]))
        cache.set(consumer.k_score0, 0)
        cache.set(consumer.k_score1, 0)

@sync_to_async
def get_info(consumer):
    try:
        consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    except ObjectDoesNotExist:
        print(f"Room with ID {consumer.room_id} does not exist.")   
        return False
    except MultipleObjectsReturned:
        print(f"Many rooms with ID {consumer.room_id} exist.")  
        return False
    try:
        consumer.player = PlayersModel.objects.get(id=consumer.player_id)
    except ObjectDoesNotExist:
        print(f"Player with ID {consumer.player_id} does not exist.")   
        return False
    except MultipleObjectsReturned:
        print(f"Many players with ID {consumer.player_id} exist.")  
        return False
    print(f"Player {consumer.player_id} connected to room {consumer.room_id}.")
    return True

@sync_to_async
def get_room_data(consumer):
    players = cache.get(consumer.k_all)
    return json.dumps({
        'ai_player': cache.get(consumer.k_ai),
        'power_play': cache.get(consumer.k_pow),
        'ball': {'x': cache.get(consumer.k_x), 'y': cache.get(consumer.k_y)},
        'players': [{'x': cache.get(str(consumer.room_id) + "_" + str(i) + "_x"),
                     'y': cache.get(str(consumer.room_id) + "_" + str(i) + "_y")} for i in players]
    })

@sync_to_async
def get_teams_data(consumer, room_id):
    team0 = cache.get(consumer.k_team0)
    team1 = cache.get(consumer.k_team1)
    return json.dumps({
        'team0': [PlayersModel.objects.get(id=i).name for i in team0],
        'team1': [PlayersModel.objects.get(id=i).name for i in team1]
        })

@sync_to_async
def get_score_data(consumer):
    return json.dumps({ 'score': [cache.get(consumer.k_score0), cache.get(consumer.k_score1)] })

@sync_to_async
def get_win_data(consumer):
    winner = ''
    winning_score = 0
    score0 = cache.get(consumer.k_score0)
    score1 = cache.get(consumer.k_score1)
    if score0 > score1:
        winner = 'player0'
        winning_score = score0
    elif score1 > score0:
        winner = 'player1'
        winning_score = score1
    return json.dumps({
        'win': winner,
        # 'score': [room.score0, room.score1],
        'score': [score0, score1],
        'winning_score': winning_score,
        'roomid': consumer.room_id
    })

@sync_to_async
def end_game(consumer):
    # print(f"Ending game in room {consumer.room_id}.")
    if cache.get(consumer.k_x) <= 0:
        cache.set(consumer.k_score1, cache.get(consumer.k_score1) + 1)
    else:
        cache.set(consumer.k_score0, cache.get(consumer.k_score0) + 1)
    cache.set(consumer.k_started, False)
    change_server(consumer)

@sync_to_async
def quit(consumer):
    all = cache.get(consumer.k_all)
    if len(all) == 0:
        return
    if len(all) == 1:
        for i in ['x', 'y', 'dx', 'dy', 'ddy', 'ai', 'pow', 'score0', 'score1', 'started', 'server', 'team0', 'team1', 'all']:
            cache.delete(getattr(consumer, "k_" + i))
        for i in ['x', 'y']:
            cache.delete(getattr(consumer, "k_player_" + i))
        consumer.room.delete()
        return
    if len(all) == 2 and cache.get(consumer.k_ai):
        # cache.set(consumer.k_ai, False)
        # try:
        #     player = PlayersModel.objects.get(login='ai')
        # except PlayersModel.DoesNotExist:
        #     print("Error: AI player not found.")
        # PlayerRoomModel.objects.get(room=consumer.room.id, player=player.id).delete()
        # time.sleep(1.01)
        for i in ['x', 'y', 'dx', 'dy', 'ddy', 'ai', 'pow', 'score0', 'score1', 'started', 'server', 'team0', 'team1', 'all']:
            cache.delete(getattr(consumer, "k_" + i))
        for i in ['x', 'y']:
            cache.delete(getattr(consumer, "k_player_" + i))
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
def change_side(consumer):
    team0 = cache.get(consumer.k_team0)
    team1 = cache.get(consumer.k_team1)
    server = cache.get(consumer.k_server)
    started = cache.get(consumer.k_started)
    if consumer.player_id in team0:
        cache.set(consumer.k_team0, team0.remove(consumer.player_id))
        cache.set(consumer.k_team1, team1.append(consumer.player_id))
        cache.set(consumer.k_player_x, pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH'])
        if not started and consumer.player_id == server:
            cache.set(consumer.k_x, consumer.server.x - pong_data['RADIUS'])
            cache.set(consumer.k_y, consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2)
            cache.set(consumer.k_dx, -1)
            cache.set(consumer.k_dy, random.choice([1, -1]))
    else:
        consumer.player.side = 0
        consumer.player.save()
        cache.set(consumer.k_player_x, pong_data['WIDTH'] - consumer.player.x - pong_data['PADDLE_WIDTH'])
        if not started and consumer.player_id == server:
            cache.set(consumer.k_x, consumer.server.x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
            cache.set(consumer.k_y, consumer.server.y + pong_data['PADDLE_HEIGHT'] / 2)
            cache.set(consumer.k_dx, 1)
            cache.set(consumer.k_dy, random.choice([1, -1]))

@sync_to_async
def change_server_async(consumer):
    change_server(consumer)

def random_choice(a, exclude):
    if len(a) == 1:
        return a[0]
    filtered = [e for e in a if e != exclude]
    return random.choice(filtered)

def change_server(consumer):
    print(f"Changing server in room {consumer.room_id}.")
    # if (PlayerRoomModel.objects.filter(room=consumer.room_id).count() > 1):
    #     condition = ~Q(id=consumer.server.id)
    #     consumer.server = PlayerRoomModel.objects.get(condition, room=consumer.room_id)
    #     cache.set(consumer.k_server, consumer.server.id)
    # else:
    #     consumer.server = PlayerRoomModel.objects.filter(room=consumer.room_id).first()
    # consumer.room.server = consumer.server.player
    server = random_choice(cache.get(consumer.k_all), cache.get(consumer.k_server))
    cache.set(consumer.k_server, server)
    x_server = cache.get(consumer.room_id + "_" + str(server) + "_x")
    y_server = cache.get(consumer.room_id + "_" + str(server) + "_y")
    team0 = cache.get(consumer.k_team0)
    if server in team0:
        cache.set(consumer.k_x, x_server + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(consumer.k_y, y_server + pong_data['PADDLE_HEIGHT'] / 2)
        cache.set(consumer.k_dx, 1)
        cache.set(consumer.k_dy, random.choice([1, -1]))
    else:
        cache.set(consumer.k_x, x_server - pong_data['RADIUS'])
        cache.set(consumer.k_y, y_server + pong_data['PADDLE_HEIGHT'] / 2)
        cache.set(consumer.k_dx, -1)
        cache.set(consumer.k_dy, random.choice([1, -1]))