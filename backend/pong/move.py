from asgiref.sync import sync_to_async
from game.models import RoomsModel, PlayerRoomModel

from .data import pong_data
import random

@sync_to_async
def check_collision(consumer, dx):
    consumer.room, consumer.players0, consumer.players1= RoomsModel.objects.get(id=consumer.room_id), PlayerRoomModel.objects.filter(room=consumer.room_id, side=0), PlayerRoomModel.objects.filter(room=consumer.room_id, side=1)
    if dx == -1:
        for p in consumer.players0:
            if consumer.room.x - pong_data['RADIUS'] == p.x + pong_data['PADDLE_WIDTH'] and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                dx = 1
                consumer.ddy = random.choice(consumer.choices)
    else:
        for p in consumer.players1:
            if consumer.room.x + pong_data['RADIUS'] == p.x and consumer.room.y >= p.y and consumer.room.y <= p.y + pong_data['PADDLE_HEIGHT']:
                dx = -1
                consumer.ddy = random.choice(consumer.choices)
    return dx

@sync_to_async
def update_ball(consumer, dx, dy):
    consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    consumer.room.x += dx * pong_data['DX']
    consumer.room.y += dy * consumer.ddy
    consumer.room.save()
    if consumer.room.y + pong_data['RADIUS'] >= pong_data['HEIGHT'] or consumer.room.y - pong_data['RADIUS'] <= 0:
        dy *= -1
    return dy

@sync_to_async
def up(consumer):
    if consumer.player.y > 0:
        consumer.player.y -= pong_data['STEP']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            consumer.room.y -= pong_data['STEP']
            consumer.room.save()

@sync_to_async
def down(consumer):
    if consumer.player.y < pong_data['HEIGHT'] - pong_data['PADDLE_HEIGHT']:
        consumer.player.y += pong_data['STEP']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            consumer.room.y += pong_data['STEP']
            consumer.room.save()

@sync_to_async
def left(consumer):
    if  (consumer.player.side == 0 and consumer.player.x > 0) \
        or (consumer.player.side == 1 and consumer.player.x > 3 * pong_data['WIDTH'] / 4):
        consumer.player.x -= pong_data['STEP_X']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            consumer.room.x -= pong_data['STEP']
            consumer.room.save()

@sync_to_async
def right(consumer):
    if (consumer.player.side == 0 and consumer.player.x < pong_data['WIDTH'] / 4 - pong_data['PADDLE_WIDTH']) \
        or (consumer.player.side == 1 and consumer.player.x < pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']):
        consumer.player.x += pong_data['STEP_X']
        consumer.player.save()
        if not consumer.room.started and consumer.server == consumer.player:
            consumer.room = RoomsModel.objects.get(id=consumer.room_id)
            consumer.room.x += pong_data['STEP']
            consumer.room.save()
