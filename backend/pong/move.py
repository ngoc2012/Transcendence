from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from game.models import RoomsModel

from .data import pong_data
import math

from django.core.cache import cache

@sync_to_async
def check_collision(consumer):
    x = cache.get(consumer.k_x)
    y = cache.get(consumer.k_y)
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    team1 = cache.get(consumer.k_team1)
    if team1 == None:
        team1 = []
    if cache.get(consumer.k_dx) == -1:
        for p in team0:
            p_x = cache.get(consumer.room_id + "_" + str(p) + "_x")
            p_y = cache.get(consumer.room_id + "_" + str(p) + "_y")
            if p_x == None or p_y == None:
                continue
            if x - pong_data['RADIUS'] == p_x + pong_data['PADDLE_WIDTH'] and y >= p_y - pong_data['PADDLE_WIDTH'] and y <= p_y + pong_data['PADDLE_HEIGHT'] + pong_data['PADDLE_WIDTH']:
                cache.set(consumer.k_dx, 1)
                i = (y - p_y -pong_data['PADDLE_HEIGHT'] / 2) / ( pong_data['PADDLE_HEIGHT'] / len(consumer.choices))
                cache.set(consumer.k_dy, math.copysign(1, i))
                i = min(math.ceil(abs(i)) + 1, len(consumer.choices) - 1)
                cache.set(consumer.k_ddy, consumer.choices[i])
    else:
        for p in team1:
            p_x = cache.get(consumer.room_id + "_" + str(p) + "_x")
            p_y = cache.get(consumer.room_id + "_" + str(p) + "_y")
            if p_x == None or p_y == None:
                continue
            if x + pong_data['RADIUS'] == p_x and y >= p_y - pong_data['PADDLE_WIDTH'] and y <= p_y + pong_data['PADDLE_HEIGHT'] + pong_data['PADDLE_WIDTH']:
                cache.set(consumer.k_dx, -1)
                i = (y - p_y - pong_data['PADDLE_HEIGHT'] / 2) / ( pong_data['PADDLE_HEIGHT'] / len(consumer.choices))
                cache.set(consumer.k_dy, math.copysign(1, i))
                i = min(math.ceil(abs(i)) + 1, len(consumer.choices) - 1)
                cache.set(consumer.k_ddy, consumer.choices[i])
                
@sync_to_async
def update_ball(consumer):
    x = cache.get(consumer.k_x) + cache.get(consumer.k_dx) * pong_data['DX']
    y = cache.get(consumer.k_y) + cache.get(consumer.k_dy) * cache.get(consumer.k_ddy)
    if y + pong_data['RADIUS'] > pong_data['HEIGHT']:
        y = pong_data['HEIGHT'] - pong_data['RADIUS']
    if y < pong_data['RADIUS']:
        y = pong_data['RADIUS']
    cache.set(consumer.k_x, x)
    cache.set(consumer.k_y, y)
    if y + pong_data['RADIUS'] == pong_data['HEIGHT'] or y == pong_data['RADIUS']:
        cache.set(consumer.k_dy, cache.get(consumer.k_dy) * -1)
        
    return x

@sync_to_async
def up(consumer):
    y = cache.get(consumer.k_player_y)
    if y == None:
        return
    if y > 0:
        cache.set(consumer.k_player_y, y - pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.player_id == cache.get(consumer.k_server):
            cache.set(consumer.k_y, cache.get(consumer.k_y) - pong_data['STEP'])

@sync_to_async
def down(consumer):
    y = cache.get(consumer.k_player_y)
    if y == None:
        return
    if y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
        cache.set(consumer.k_player_y, y + pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.player_id == cache.get(consumer.k_server):
            cache.set(consumer.k_y, cache.get(consumer.k_y) + pong_data['STEP'])

@sync_to_async
def left(consumer):
    x = cache.get(consumer.k_player_x)
    if x == None:
        return
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    if (consumer.player_id in team0 and x > 0) \
        or (consumer.player_id not in team0 and x > 3 * pong_data['WIDTH'] / 4):
        cache.set(consumer.k_player_x, x - pong_data['STEP_X'])
        if not cache.get(consumer.k_started) and consumer.player_id == cache.get(consumer.k_server):
            cache.set(consumer.k_x, cache.get(consumer.k_x) - pong_data['STEP_X'])

@sync_to_async
def right(consumer):
    x = cache.get(consumer.k_player_x)
    if x == None:
        return
    team0 = cache.get(consumer.k_team0)
    if team0 == None:
        team0 = []
    if (consumer.player_id in team0 and x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
        or (consumer.player_id not in team0 and x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
        cache.set(consumer.k_player_x, x + pong_data['STEP_X'])
        if not cache.get(consumer.k_started) and consumer.player_id == cache.get(consumer.k_server):
            cache.set(consumer.k_x, cache.get(consumer.k_x) + pong_data['STEP_X'])
