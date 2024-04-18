import json
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import PlayersModel

import asyncio
from game.models import RoomsModel, TournamentMatchModel, TournamentModel
from .data import pong_data
from .move import check_collision, update_ball, up, down, left, right
from .game import get_info, get_room_data, get_teams_data, get_score_data, end_game, quit, change_side, get_win_data, change_server_async, set_power_play, game_init
from .ai_player import ai_player
from django.core.cache import cache

@database_sync_to_async
def rematch(consumer):
    try:
        room = consumer.room
        match = TournamentMatchModel.objects.get(room_uuid=room.id)
        tournament = match.tournament

        if tournament.rematchIP:
            return
        
        new_room =  RoomsModel.objects.create(
            game=tournament.game,
            name=f"{tournament.name} - Match {tournament.total_matches}",
            owner=tournament.owner,
            tournamentRoom=True
        )
        cache.set(str(new_room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(str(new_room.id) + "_y", pong_data['HEIGHT'] / 2)

        match_data = {field.name: getattr(match, field.name) for field in match._meta.fields if field.name != 'id' and field.name != 'room' and field.name != 'room_uuid'}
        match_data['room'] = new_room
        match_data['room_uuid'] = new_room.id

        new_match = TournamentMatchModel.objects.create(**match_data)
        match.delete()
        tournament.rematchIP = True
        tournament.save()

        return new_match
    except TournamentMatchModel.DoesNotExist:
        print("Match not found")
    except Exception as e:
        print(f"An error occurred: {e}")


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.player_id = int(self.scope['url_route']['kwargs']['player_id']) # 1, 2, 3 ...
        self.choices = [1, 2, 5, 10]
        self.room = await get_room_by_id(self.room_id)
        self.player = await get_user_by_id(self.player_id)
        self.player0: PlayersModel = await get_player0(self.room)
        self.player1: PlayersModel = await get_player1(self.room)
        for i in ['x', 'y', 'dx', 'dy', 'ddy', 'ai', 'pow', 'score0', 'score1', 'started', 'server', 'team0', 'team1', 'all']:
            setattr(self, "k_" + i, str(self.room_id) + "_" + i)
        for i in ['x', 'y']:
            setattr(self, "k_player_" + i, str(self.room_id) + "_" + str(self.player_id) + "_" + i)
        
        check = await get_info(self)
        if self.player0:
            self.player0.online_status = 'In-game'
            self.player0.save()
        if self.player1:
            self.player1.online_status = 'In-game'
            self.player1.save()
        if not check:
            self.disconnect(1011)
        await game_init(self)
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
        score0 = cache.get(self.k_score0)
        score1 = cache.get(self.k_score1)
        if self.room.tournamentRoom and score0 is None or score1 is None or score0 < 11 and score1 < 11:
            await rematch(self)
        await quit(self)
        await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    async def receive(self, text_data):
        if text_data == 'start':
            players = cache.get(self.k_all)
            if players == None or len(players) < 2:
                return
            info = await get_info(self)
            if info and not cache.get(self.k_started):
                asyncio.create_task(self.game_loop())
        elif text_data == 'left':
            await left(self)
        elif text_data == 'right':
            await right(self)
        elif text_data == 'up':
            await up(self)
        elif text_data == 'down':
            await down(self)
        elif text_data == 'power':
            await set_power_play(self)
        elif text_data == 'ai_player':
            await ai_player(self)
        elif text_data == 'quit':
            next
        elif text_data == 'side':
            await change_side(self)
            await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        elif text_data == 'teams':
            await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        elif text_data == 'server':
            await change_server_async(self)
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
        room_data = await get_room_data(self)
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
        score = await get_score_data(self)
        if score is None:
            self.disconnect(1011)
            return
        await self.send(text_data=score)

    async def win_data(self, event):
        win = await get_win_data(self)
        await self.send(text_data=win)

    async def game_loop(self):
        print("Game in room {self.room_id} started.")
        cache.set(self.k_started, True)
        while True:
            await asyncio.sleep(0.02)
            players = cache.get(self.k_all)
            if players == None or len(players) == 0:
                await quit(self)
                await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
                return
            x = await update_ball(self)
            if x <= 0 or x >= pong_data['WIDTH']:
                await end_game(self)
                await self.channel_layer.group_send(self.room_id, {'type': 'score_data'})
                await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
                # # Adding rules for tournament: first at 11 and win by 2 points:
                # if self.room.tournamentRoom == True and (self.room.score1 >= 11 and self.room.score0 <= self.room.score1 - 2) or \
                # (self.room.score0 >= 11 and self.room.score1 <= self.room.score0 - 2):
                # if self.room.tournamentRoom == True and self.room.score0 == 1 or self.room.score1 == 1:
                score0 = cache.get(self.k_score0)
                score1 = cache.get(self.k_score1)
                # if abs(score0 - score1) > 1 and (score0 >= 1 or score1 >= 1) :
                if (score0 >= 1 or score1 >= 1) :
                    await self.channel_layer.group_send(self.room_id, {'type': 'win_data'})
                    if self.room.tournamentRoom == False:
                        if score0 > score1:
                            self.player0.history += 'W'
                            self.player1.history += 'L'
                            self.player0.score_history += str(score0) + '-' + str(score1)
                            self.player1.score_history += str(score0) + '-' + str(score1)
                            self.player0.save()
                            self.player1.save()
                        else:
                            self.player0.history += 'L'
                            self.player1.history += 'W'
                            self.player0.score_history += str(score0) + '-' + str(score1)
                            self.player1.score_history += str(score0) + '-' + str(score1)
                            self.player0.save()
                            self.player1.save()
                        return
            await check_collision(self)
            await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})

@database_sync_to_async
def get_room_by_id(id) -> RoomsModel:
    return RoomsModel.objects.get(id=id)

@database_sync_to_async
def get_user_by_id(id) -> PlayersModel:
    return PlayersModel.objects.get(id=id)

@database_sync_to_async
def get_player0(room) -> PlayersModel:
    return room.player0

@database_sync_to_async
def get_player1(room) -> PlayersModel:
    return room.player1

@database_sync_to_async
def save_player(player):
    player.save()
    return player