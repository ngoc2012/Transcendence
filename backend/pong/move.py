from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from game.models import RoomsModel, PlayerRoomModel

from .data import pong_data
import random

from django.core.cache import cache

@sync_to_async
def check_collision(consumer):
    try:
        consumer.room, consumer.players0, consumer.players1= RoomsModel.objects.get(id=consumer.room_id), PlayerRoomModel.objects.filter(room=consumer.room_id, side=0), PlayerRoomModel.objects.filter(room=consumer.room_id, side=1)
        x = cache.get(consumer.k_x)
        y = cache.get(consumer.k_y)
        if cache.get(consumer.k_dx) == -1:
            for p in consumer.players0:
                # if consumer.room.x - pong_data['RADIUS'] == p.x + pong_data['PADDLE_WIDTH'] and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                #     consumer.room.dx = 1
                #     consumer.ddy = random.choice(consumer.choices)
                p_x = cache.get(consumer.room_id + "_" + str(p.id) + "_x")
                p_y = cache.get(consumer.room_id + "_" + str(p.id) + "_y")
                if x - pong_data['RADIUS'] == p_x + pong_data['PADDLE_WIDTH'] and y >= p_y and y <= p_y + pong_data['PADDLE_HEIGHT']:
                    cache.set(consumer.k_dx, 1)
                    cache.set(consumer.k_ddy, random.choice(consumer.choices))
        else:
            for p in consumer.players1:
                p_x = cache.get(consumer.room_id + "_" + str(p.id) + "_x")
                p_y = cache.get(consumer.room_id + "_" + str(p.id) + "_y")
                # if consumer.room.x + pong_data['RADIUS'] == p.x and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                #     consumer.room.dx = -1
                #     consumer.ddy = random.choice(consumer.choices)
                if x + pong_data['RADIUS'] == p_x and y >= p_y and y <= p_y + pong_data['PADDLE_HEIGHT']:
                    cache.set(consumer.k_dx, -1)
                    cache.set(consumer.k_ddy, random.choice(consumer.choices))
    except ObjectDoesNotExist:
        next

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
        if not consumer.room.started and consumer.server == consumer.player:
            cache.set(consumer.k_y, cache.get(consumer.k_y) - pong_data['STEP'])

@sync_to_async
def down(consumer):
    y = cache.get(consumer.k_player_y)
    if y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
        cache.set(consumer.k_player_y, y + pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            cache.set(consumer.k_y, cache.get(consumer.k_y) + pong_data['STEP'])

@sync_to_async
def left(consumer):
    x = cache.get(consumer.k_player_x)
    if  (consumer.player.side == 0 and x > 0) \
        or (consumer.player.side == 1 and x > 3 * pong_data['WIDTH'] / 4):
        cache.set(consumer.k_player_x, x - pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            cache.set(consumer.k_x, cache.get(consumer.k_x) - pong_data['STEP'])

@sync_to_async
def right(consumer):
    x = cache.get(consumer.k_player_x)
    if (consumer.player.side == 0 and x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
        or (consumer.player.side == 1 and x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
        cache.set(consumer.k_player_x, x + pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            cache.set(consumer.k_x, cache.get(consumer.k_x) + pong_data['STEP'])
