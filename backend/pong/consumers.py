import json
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from accounts.models import PlayersModel
import datetime

import asyncio
from game.models import RoomsModel, TournamentMatchModel, TournamentModel, MatchModel
from .data import pong_data
from .move import check_collision, update_ball, up, down, left, right
from .game import get_info, get_room_data, get_teams_data, get_score_data, end_game, quit, change_side, get_win_data, change_server_async, set_power_play, game_init
from .ai_player import ai_player
from django.core.cache import cache

@database_sync_to_async
def rematch(self):
    try:
        print('entering rematch')
        tournament = TournamentModel.objects.get(id=self.tour_id)
        if tournament.rematchIP:
            return
        
        tournament.rematchIP = True
        tournament.save()

        match = TournamentMatchModel.objects.filter(tournament=tournament).order_by('-match_number').first()
        
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
        self.tour_id = False
        self.terminated = False
        self.disconnected = False
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
        self.disconnected = True
        print(f"Player {self.player_id} disconnected with code {close_code}.")
        score0 = cache.get(self.k_score0)
        score1 = cache.get(self.k_score1)
        await self.channel_layer.group_send(self.room_id, {'type': 'teams_data'})
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )
        await quit(self)
        if self.tour_id and not self.terminated:
            await rematch(self)

    async def receive(self, text_data):
        if text_data == 'start':
            players = cache.get(self.k_all)
            if players == None or len(players) < 2:
                return
            if self.player_id != cache.get(self.k_server) and not cache.get(self.k_ai):
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
            players = cache.get(self.k_all)
            # print(cache.get(self.k_ai), len(players))
            ai = cache.get(self.k_ai)
            if (ai == None or ai == False) and len(players) > 1:
                return
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
        elif text_data == 'stop':
            self.terminated = True
        elif text_data.startswith('tour_id:'):
            self.tour_id = text_data.split('tour_id:')[1]
        await self.channel_layer.group_send(self.room_id, {'type': 'group_data'})
        self.player0: PlayersModel = await get_player0(self.room)
        self.player1: PlayersModel = await get_player1(self.room)
    
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
                score0 = cache.get(self.k_score0)
                score1 = cache.get(self.k_score1)
                if (score0 >= 2 or score1 >= 2) :
                # if abs(score0 - score1) > 1 and (score0 >= 11 or score1 >= 11) :
                    if not self.disconnected:
                        await self.channel_layer.group_send(self.room_id, {'type': 'win_data'})
                    if self.room.tournamentRoom == False:
                        if score0 > score1 and cache.get(self.k_ai) == False:
                            match0 = MatchModel(id=MatchModel.objects.count(), opp=self.player1.login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='W')
                            match1 = MatchModel(id=MatchModel.objects.count(), opp=self.player1.login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='L')
                            match0.save()
                            match1.save()
                            self.player0.history.add(match0)
                            self.player1.history.add(match1)
                            self.player0.save()
                            self.player1.save()
                        elif cache.get(self.k_ai) == False:
                            match0 = MatchModel(id=MatchModel.objects.count(), opp=self.player1.login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='L')
                            match1 = MatchModel(id=MatchModel.objects.count(), opp=self.player1.login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='W')
                            match0.save()
                            match1.save()
                            self.player0.history.add(match0)
                            self.player1.history.add(match1)
                            self.player0.save()
                            self.player1.save()
                        elif score0 > score1 and cache.get(self.k_ai) == True:
                            match = MatchModel(id=MatchModel.objects.count(), opp=PlayersModel.objects.get(login='ai').login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='W')
                            match.save()
                            self.player0.history.add(match)
                            self.player0.save()
                        else:
                            match = MatchModel(id=MatchModel.objects.count(), opp=PlayersModel.objects.get(login='ai').login, score=str(str(score0) + '-' + str(score1)), date=datetime.date.today(), result='L')
                            match.save()
                            self.player0.history.add(match)
                            self.player0.save()
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