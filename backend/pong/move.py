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
        if cache.get(consumer.k_dx) == -1:
            for p in consumer.players0:
                # if consumer.room.x - pong_data['RADIUS'] == p.x + pong_data['PADDLE_WIDTH'] and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                #     consumer.room.dx = 1
                #     consumer.ddy = random.choice(consumer.choices)
                if cache.get(consumer.k_x) - pong_data['RADIUS'] == p.x + pong_data['PADDLE_WIDTH'] and cache.get(consumer.k_y) >= p.y and cache.get(consumer.k_y) <= p.y + pong_data['PADDLE_HEIGHT']:
                    cache.set(consumer.k_dx, 1)
                    cache.set(consumer.k_ddy, random.choice(consumer.choices))
        else:
            for p in consumer.players1:
                # if consumer.room.x + pong_data['RADIUS'] == p.x and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                #     consumer.room.dx = -1
                #     consumer.ddy = random.choice(consumer.choices)
                if cache.get(consumer.k_x) + pong_data['RADIUS'] == p.x and cache.get(consumer.k_y) >= p.y and cache.get(consumer.k_y) <= p.y + pong_data['PADDLE_HEIGHT']:
                    cache.set(consumer.k_dx, -1)
                    cache.set(consumer.k_ddy, random.choice(consumer.choices))
    except ObjectDoesNotExist:
        next

@sync_to_async
def update_ball(consumer):
    # consumer.room.x += consumer.room.dx * pong_data['DX']
    # consumer.room.y += consumer.room.dy * consumer.ddy
    cache.set(consumer.k_x, cache.get(consumer.k_x) + cache.get(consumer.k_dx) * pong_data['DX'])
    cache.set(consumer.k_y, cache.get(consumer.k_x) + cache.get(consumer.k_dy) * cache.get(consumer.k_ddy))
    
    # if consumer.room.y + pong_data['RADIUS'] >= pong_data['HEIGHT'] or consumer.room.y - pong_data['RADIUS'] <= 0:
    #     consumer.room.dy *= -1
    # consumer.room.save()
    if cache.get(consumer.k_y) + pong_data['RADIUS'] >= pong_data['HEIGHT'] or cache.get(consumer.k_y) - pong_data['RADIUS'] <= 0:
        cache.set(consumer.k_dy, cache.get(consumer.k_dy) * -1)

@sync_to_async
def up(consumer):
    y = cache.get(consumer.k_player_y)
    # if consumer.player.y > 0:
    if y > 0:
        # consumer.player.y -= pong_data['STEP']
        # consumer.player.save()
        cache.set(consumer.k_player_y, y - pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            #consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            #consumer.room.y -= pong_data['STEP']
            cache.set(consumer.k_y, cache.get(consumer.k_y) - pong_data['STEP'])
            #consumer.room.save()

@sync_to_async
def down(consumer):
    y = cache.get(consumer.k_player_y)
    # if consumer.player.y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
    if y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
        # consumer.player.y += pong_data['STEP']
        # consumer.player.save()
        cache.set(consumer.k_player_y, y + pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            #consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            #consumer.room.y += pong_data['STEP']
            cache.set(consumer.k_y, cache.get(consumer.k_y) + pong_data['STEP'])
            #consumer.room.save()

@sync_to_async
def left(consumer):
    x = cache.get(consumer.k_player_x)
    if  (consumer.player.side == 0 and x > 0) \
        or (consumer.player.side == 1 and x > 3 * pong_data['WIDTH'] / 4):
        # consumer.player.x -= pong_data['STEP_X']
        # consumer.player.save()
        cache.set(consumer.k_player_x, x - pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            #consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            #consumer.room.x -= pong_data['STEP']
            cache.set(consumer.k_x, cache.get(consumer.k_x) - pong_data['STEP'])
            #consumer.room.save()

@sync_to_async
def right(consumer):
    x = cache.get(consumer.k_player_x)
    if (consumer.player.side == 0 and x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
        or (consumer.player.side == 1 and x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
        # consumer.player.x += pong_data['STEP_X']
        # consumer.player.save()
        cache.set(consumer.k_player_x, x + pong_data['STEP'])
        if not consumer.room.started and consumer.server == consumer.player:
            #consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            #consumer.room.x += pong_data['STEP']
            cache.set(consumer.k_x, cache.get(consumer.k_x) + pong_data['STEP'])
            #consumer.room.save()
