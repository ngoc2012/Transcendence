import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayerRoomModel, PlayersModel

import asyncio

from .data import pong_data
from .move import check_collision, update_ball, up, down, left, right
from .game import get_info, get_room_data, get_teams_data, get_score_data, start_game, end_game, quit, change_side
import random

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
        await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'score_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    async def receive(self, text_data):
        if text_data == 'start':
            self.room = RoomsModel.objects.get(id=room_id)
            if not self.room.started:
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
            await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        elif text_data == 'side':
            await change_side(self)
            await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
    
    async def group_data(self, event):
        players = PlayerRoomModel.objects.filter(room=self.room_id)
        room_data = await get_room_data(players, self.room_id)
        await self.send(text_data=room_data)
    
    async def teams_data(self, event):
        teams = await get_teams_data(self.room_id)
        await self.send(text_data=teams)

    async def score_data(self, event):
        score = await get_score_data(self.room_id)
        await self.send(text_data=score)

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
                await self.channel_layer.group_send(self.room_id, {'type': 'score_data'})
                await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
                return            
            await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
