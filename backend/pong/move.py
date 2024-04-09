from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from game.models import RoomsModel, PlayerRoomModel

from .data import pong_data
import random

from django.core.cache import cache

@sync_to_async
def check_collision(consumer):
    x = cache.get(consumer.k_x)
    y = cache.get(consumer.k_y)
    team0 = cache.get(consumer.k_team0)
    team1 = cache.get(consumer.k_team1)
    if cache.get(consumer.k_dx) == -1:
        for p in team0:
            p_x = cache.get(consumer.room_id + "_" + str(p) + "_x")
            p_y = cache.get(consumer.room_id + "_" + str(p) + "_y")
            if x - pong_data['RADIUS'] == p_x + pong_data['PADDLE_WIDTH'] and y >= p_y and y <= p_y + pong_data['PADDLE_HEIGHT']:
                cache.set(consumer.k_dx, 1)
                cache.set(consumer.k_ddy, random.choice(consumer.choices))
    else:
        for p in team1:
            p_x = cache.get(consumer.room_id + "_" + str(p) + "_x")
            p_y = cache.get(consumer.room_id + "_" + str(p) + "_y")
            if x + pong_data['RADIUS'] == p_x and y >= p_y and y <= p_y + pong_data['PADDLE_HEIGHT']:
                cache.set(consumer.k_dx, -1)
                cache.set(consumer.k_ddy, random.choice(consumer.choices))

@sync_to_async
def update_ball(consumer):
    x = cache.get(consumer.k_x) + cache.get(consumer.k_dx) * pong_data['DX']
    y = cache.get(consumer.k_y) + cache.get(consumer.k_dy) * cache.get(consumer.k_ddy)
    cache.set(consumer.k_x, x)
    cache.set(consumer.k_y, y)
    if y + pong_data['RADIUS'] >= pong_data['HEIGHT'] or y - pong_data['RADIUS'] <= 0:
        cache.set(consumer.k_dy, cache.get(consumer.k_dy) * -1)
    return x

@sync_to_async
def up(consumer):
    y = cache.get(consumer.k_player_y)
    if y > 0:
        cache.set(consumer.k_player_y, y - pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.server == consumer.player_id:
            cache.set(consumer.k_y, cache.get(consumer.k_y) - pong_data['STEP'])

@sync_to_async
def down(consumer):
    y = cache.get(consumer.k_player_y)
    if y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
        cache.set(consumer.k_player_y, y + pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.server == consumer.player_id:
            cache.set(consumer.k_y, cache.get(consumer.k_y) + pong_data['STEP'])

@sync_to_async
def left(consumer):
    x = cache.get(consumer.k_player_x)
    team0 = cache.get(consumer.k_team0)
    if  (consumer.player_id in team0 and x > 0) \
        or (consumer.player_id not in team0 and x > 3 * pong_data['WIDTH'] / 4):
        cache.set(consumer.k_player_x, x - pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.server == consumer.player_id:
            cache.set(consumer.k_x, cache.get(consumer.k_x) - pong_data['STEP'])

@sync_to_async
def right(consumer):
    x = cache.get(consumer.k_player_x)
    team0 = cache.get(consumer.k_team0)
    if (consumer.player_id in team0 and x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
        or (consumer.player_id not in team0 and x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
        cache.set(consumer.k_player_x, x + pong_data['STEP'])
        if not cache.get(consumer.k_started) and consumer.server == consumer.player_id:
            cache.set(consumer.k_x, cache.get(consumer.k_x) + pong_data['STEP'])
