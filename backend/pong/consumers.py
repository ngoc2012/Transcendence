import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayerRoomModel
from accounts.models import PlayersModel

import asyncio

from .data import pong_data
from .move import check_collision, update_ball, up, down, left, right
from .game import get_info, get_room_data, get_teams_data, get_score_data, start_game, end_game, quit, change_side, change_server_direction, remove_player, check_player, get_win_data, get_room_by_id
import random

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.choices = [5, 10]
        self.dx = 1
        self.dy = 1
        self.ddy = random.choice(self.choices)
        self.room = None
        self.player = None
        self.server = None
        self.players0 = None
        self.players1 = None
        
        check = await get_info(self)
        if not check:
            self.disconnect(1011)
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'score_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})

    async def disconnect(self, close_code):
        # https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
        # 1000: Normal closure.
        # 1001: Going away.
        # 1006: Abnormal closure (such as a server crash).
        # 1008: Policy violation.
        # 1011: Internal error.
        print(f"Player {self.player_id} disconnected with code {close_code}.")
        await quit(self)
        await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    async def receive(self, text_data):
        if text_data == 'start':
            info = await get_info(self)
            if info and not self.room.started:
                asyncio.create_task(self.game_loop())
                if self.room.tournamentRoom:
                    await self.send(text_data=json.dumps({
                        text_data: "tour_match_start"
                    }))
        elif text_data == 'left':
            await left(self)
        elif text_data == 'right':
            await right(self)
        elif text_data == 'up':
            await up(self)
        elif text_data == 'down':
            await down(self)
        elif text_data == 'quit':
            next
        elif text_data == 'side':
            await change_side(self)
            await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        elif text_data == 'server':
            await change_server_direction(self)
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
    
    async def close_connection(self, data):
        await self.send(text_data=json.dumps({
            "type": 'close',
            "player_id": data['player_id']
        }))

    async def start(self, data):
        await self.send(text_data=json.dumps({
            "type": 'start'
        }))

    async def group_data(self, event):
        players = PlayerRoomModel.objects.filter(room=self.room_id)
        room_data = await get_room_data(players, self.room_id)
        if room_data is None:
            self.disconnect(1011)
            return
        await self.send(text_data=room_data)
    
    async def teams_data(self, event):
        teams = await get_teams_data(self, self.room_id)
        if teams is None:
            self.disconnect(1011)
            return
        await self.send(text_data=teams)

    async def score_data(self, event):
        score = await get_score_data(self.room_id)
        if score is None:
            self.disconnect(1011)
            return
        await self.send(text_data=score)

    async def win_data(self, event):
        win = await get_win_data(self.room_id)
        await self.send(text_data=win)

    async def game_loop(self):
        start = await start_game(self)
        if not start:
            self.disconnect(1011)
            return
        dx = self.dx
        dy = self.dy
        while True:
            await asyncio.sleep(0.02)
            check = await check_player(self)
            if not check:
                await quit(self)
                await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
                return
            dy = await update_ball(self, dx, dy)
            dx = await check_collision(self, dx)
            if self.room.x <= 0 or self.room.x >= pong_data['WIDTH']:
                await end_game(self)
                await self.channel_layer.group_send(self.room_id, {'type': 'score_data'})
                await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
                # # Adding rules for tournament: first at 11 and win by 2 points:
                # if self.room.tournamentRoom == True and (self.room.score1 >= 11 and self.room.score0 <= self.room.score1 - 2) or \
                # (self.room.score0 >= 11 and self.room.score1 <= self.room.score0 - 2):
                if self.room.tournamentRoom == True and self.room.score0 == 1 or self.room.score1 == 1:
                    await self.channel_layer.group_send(self.room_id, {'type': 'win_data'})
                return            
            await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
