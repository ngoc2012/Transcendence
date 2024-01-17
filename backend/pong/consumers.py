import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayerRoomModel

import asyncio

from .data import pong_data
from .move import check_collision, update_ball, up, down, left, right
import random

@sync_to_async
def get_info(consumer):
    consumer.room = RoomsModel.objects.get(id=consumer.room_id)
    consumer.player = PlayerRoomModel.objects.get(id=consumer.player_id)
    consumer.server = PlayerRoomModel.objects.get(player=consumer.room.server)

@sync_to_async
def get_room_data(players, room_id):
    room = RoomsModel.objects.get(id=room_id)
    return json.dumps({
        'score': [room.score0, room.score1],
        'ball': {'x': room.x, 'y':room.y},
        'players': [{'x': i.x, 'y': i.y} for i in players]
    })

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
        consumer.server = PlayerRoomModel.objects.filter(room=consumer.room_id).first()
        #consumer.room.server = PlayersModel.objects.get(player=consumer.room.server)
        #consumer.room.save()
    else:
        print("Player deleted")
        consumer.player.delete()

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.choices = [5, 10]
        self.ddy = random.choice(self.choices)
        self.room = None
        self.player = None
        self.server = None
        self.players0 = None
        self.players1 = None
        await get_info(self)
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    async def receive(self, text_data):
        #print(text_data)
        if text_data == 'start' and not self.room.started:
            asyncio.create_task(self.game_loop())
        elif text_data == 'left':
            await left(self)
        elif text_data == 'right':
            await right(self)
        elif text_data == 'up':
            await up(self)
        elif text_data == 'down':
            await down(self)
        elif text_data == 'quit':
            await quit(self)
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
    
    async def group_data(self, event):
        players = PlayerRoomModel.objects.filter(room=self.room_id)
        room_data = await get_room_data(players, self.room_id)
        await self.send(text_data=room_data)
    
    async def game_loop(self):
        await start_game(self)
        dx = 1
        dy = 1
        while True:
            await asyncio.sleep(0.02)
            dy = await update_ball(self, dx, dy)
            dx = await check_collision(self, dx)
            if self.room.x <= 0 or self.room.x >= pong_data['WIDTH']:
                await end_game(self)
                await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
                return            
            await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
