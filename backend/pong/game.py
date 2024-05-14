from django.core.exceptions import ObjectDoesNotExist
import json
from asgiref.sync import sync_to_async
from game.models import RoomsModel
from accounts.models import PlayersModel

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.cache import cache

from asgiref.sync import sync_to_async

import random
import json

from .data import pong_data

@sync_to_async
def set_power_play(consumer):
    if cache.get(consumer.k_pow):
        cache.set(consumer.k_pow, False)
        team0 = cache.get(consumer.k_team0)
        team1 = cache.get(consumer.k_team1)
        if team0 == None:
            team0 = []
        if team1 == None:
            team1 = []
        started = cache.get(consumer.k_started)
        server = cache.get(consumer.k_server)
        for i in team0 + team1:
            if i in team0:
                cache.set(consumer.room_id + "_" + str(i) + "_x", 0)
            else:
                cache.set(consumer.room_id + "_" + str(i) + "_x", pong_data['WIDTH'] - pong_data['PADDLE_WIDTH'])
            if not started and i == server:
                if i in team0:
                    cache.set(consumer.k_x, pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
                else:
                    cache.set(consumer.k_x, pong_data['WIDTH'] - pong_data['PADDLE_WIDTH'] - pong_data['RADIUS'])
    else:
        cache.set(consumer.k_pow, True)

@sync_to_async
def game_init(consumer):
    if cache.get(consumer.k_started) == None:
        cache.set(consumer.k_server, consumer.player_id)
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
        return False
    except MultipleObjectsReturned:
        return False
    try:
        consumer.player = PlayersModel.objects.get(id=consumer.player_id)
    except ObjectDoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False
    return True

@sync_to_async
def get_room_data(consumer):
    players = cache.get(consumer.k_all)
    if players == None:
        players = []
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
    if team0 == None:
        team0 = []
    team1 = cache.get(consumer.k_team1)
    if team1 == None:
        team1 = []
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
        'score': [score0, score1],
        'winning_score': winning_score,
        'roomid': consumer.room_id
    })

@sync_to_async
def end_game(consumer):
    if cache.get(consumer.k_x) <= 0:
        cache.set(consumer.k_score1, cache.get(consumer.k_score1) + 1)
    else:
        cache.set(consumer.k_score0, cache.get(consumer.k_score0) + 1)
    cache.set(consumer.k_started, False)
    change_server(consumer)

def remove_player(consumer, player_id):
    players = cache.get(consumer.k_all)
    if players == None:
        players = []
    players.remove(player_id)
    cache.set(consumer.k_all, players)
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    if player_id in team0:
        team0.remove(player_id)
        cache.set(consumer.k_team0, team0)
    else:
        cache.set(consumer.k_team1, cache.get(consumer.k_team1).remove(player_id))
    if player_id == cache.get(consumer.k_server):
        change_server(consumer)

@sync_to_async
def quit(consumer):
    players = cache.get(consumer.k_all)
    if players == None or len(players) == 0:
        return

    if len(players) == 1:
        for i in ['x', 'y', 'dx', 'dy', 'ddy', 'ai', 'pow', 'score0', 'score1', 'started', 'server', 'team0', 'team1', 'all']:
            cache.delete(getattr(consumer, "k_" + i))
        for i in ['x', 'y']:
            cache.delete(getattr(consumer, "k_player_" + i))
        consumer.room.delete()
        return
    if len(players) == 2 and cache.get(consumer.k_ai):
        for i in ['x', 'y', 'dx', 'dy', 'ddy', 'ai', 'pow', 'score0', 'score1', 'started', 'server', 'team0', 'team1', 'all']:
            cache.delete(getattr(consumer, "k_" + i))
        for i in ['x', 'y']:
            cache.delete(getattr(consumer, "k_player_" + i))
        consumer.room.delete()
        return
    remove_player(consumer, consumer.player_id)

@sync_to_async
def change_side(consumer):
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    team1 = cache.get(consumer.k_team1)
    if team1 == None:
        team1 = []
    server = cache.get(consumer.k_server)
    started = cache.get(consumer.k_started)
    # x_server = cache.get(consumer.room_id + "_" + str(server) + "_x")
    # y_server = cache.get(consumer.room_id + "_" + str(server) + "_y")
    if consumer.player_id in team0:
        team0.remove(consumer.player_id)
        cache.set(consumer.k_team0, team0)
        team1.append(consumer.player_id)
        cache.set(consumer.k_team1, team1)
        cache.set(consumer.k_player_x, pong_data['WIDTH'] - cache.get(consumer.k_player_x) - pong_data['PADDLE_WIDTH'])
        player_x = cache.get(consumer.k_player_x)
        player_y = cache.get(consumer.k_player_y)
        if not started and consumer.player_id == server:
            cache.set(consumer.k_x, player_x - pong_data['RADIUS'])
            cache.set(consumer.k_y, player_y + pong_data['PADDLE_HEIGHT'] / 2)
            cache.set(consumer.k_dx, -1)
            # cache.set(consumer.k_dy, random.choice([1, -1]))
    elif consumer.player_id in team1:
        team1.remove(consumer.player_id)
        cache.set(consumer.k_team1, team1)
        team0.append(consumer.player_id)
        cache.set(consumer.k_team0, team0)
        cache.set(consumer.k_player_x, pong_data['WIDTH'] - cache.get(consumer.k_player_x) - pong_data['PADDLE_WIDTH'])
        player_x = cache.get(consumer.k_player_x)
        player_y = cache.get(consumer.k_player_y)
        if not started and consumer.player_id == server:
            cache.set(consumer.k_x, player_x + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
            cache.set(consumer.k_y, player_y + pong_data['PADDLE_HEIGHT'] / 2)
            cache.set(consumer.k_dx, 1)
            # cache.set(consumer.k_dy, random.choice([1, -1]))
    cache.set(consumer.k_dy, random.choice([1, -1]))
    cache.set(consumer.k_ddy, random.choice(consumer.choices))

@sync_to_async
def change_server_async(consumer):
    change_server(consumer)

def random_choice(a, exclude):
    if len(a) == 1:
        return a[0]
    filtered = [e for e in a if e != exclude]
    return random.choice(filtered)

def change_server(consumer):
    players = cache.get(consumer.k_all)
    if players == None or len(players) == 0:
        return
    server = random_choice(cache.get(consumer.k_all), cache.get(consumer.k_server))
    cache.set(consumer.k_server, server)
    x_server = cache.get(consumer.room_id + "_" + str(server) + "_x")
    y_server = cache.get(consumer.room_id + "_" + str(server) + "_y")
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    if server in team0:
        cache.set(consumer.k_x, x_server + pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(consumer.k_dx, 1)
    else:
        cache.set(consumer.k_x, x_server - pong_data['RADIUS'])
        cache.set(consumer.k_dx, -1)
    cache.set(consumer.k_y, y_server + pong_data['PADDLE_HEIGHT'] / 2)
    cache.set(consumer.k_dy, random.choice([1, -1]))
    cache.set(consumer.k_ddy, random.choice(consumer.choices))