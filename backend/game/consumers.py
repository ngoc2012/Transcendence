import json, random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import RoomsModel, TournamentModel, TournamentMatchModel
from accounts.models import PlayersModel
from pong.data import pong_data
from django.utils import timezone
from django.db.models import Q
import requests
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings

@database_sync_to_async
def get_user_from_login(login):
    try:
        user = get_user_model().objects.get(login=login)
        return user
    except(get_user_model().DoesNotExist) as e:
        return None

@database_sync_to_async
def get_user_from_token(token):
    try:
        user = get_user_model().objects.get(ws_token=token)
        return user
    except(get_user_model().DoesNotExist) as e:
        return None

@sync_to_async
def room_list(rooms):
    return json.dumps([
        {
            "id": str(i),
            "name": i.name
            } for i in rooms])

@sync_to_async
def close_connection(data):
    print(data['login_id'])
    return json.dumps({
        "type": 'close',
        "login_id": data['login_id']
    })

@database_sync_to_async
def get_player_by_login(login):
    return PlayersModel.objects.filter(login=login).first()

@database_sync_to_async
def get_player_by_id(id):
    return PlayersModel.objects.filter(id=id).first()

@database_sync_to_async
def get_room_by_id(roomId):
    return RoomsModel.objects.filter(id=roomId).first()

@database_sync_to_async
def get_match_by_room(room):
    return TournamentMatchModel.objects.filter(room=room).select_related('tournament', 'player1', 'player2').first()

@database_sync_to_async
def get_connected_players(connected_user_ids):
    return list(PlayersModel.objects.filter(id__in=connected_user_ids).values('id', 'login', 'name'))
def check_player_in_tournament(player):
    tournament = TournamentModel.objects.filter(
      owner=player, terminated=False).select_related('owner').distinct().first()
    return tournament

@database_sync_to_async
def get_tournament(tour_id):
    try:
        return TournamentModel.objects.select_related('owner', 'winner').get(id=tour_id)
    except TournamentModel.DoesNotExist:
        return None
    
@database_sync_to_async
def get_user_from_token(token):
    try:
        user = get_user_model().objects.get(ws_token=token)
        return user
    except(get_user_model().DoesNotExist) as e:
        return None
    
@database_sync_to_async
def get_connected_players(connected_user_ids):
    return list(PlayersModel.objects.filter(id__in=connected_user_ids).values('id', 'login', 'name'))

class RoomsConsumer(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
                 
        self.group_name = "rooms"
        self.login = ''
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_room_list'
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        if hasattr(self, 'user_id'):
            unique_group_name = f"user_{self.user_id}"
            await self.channel_layer.group_discard(unique_group_name, self.channel_name)
        user_id = getattr(self, 'user_id', None)
        if user_id in RoomsConsumer.connected_users:
            RoomsConsumer.connected_users.remove(user_id)
            await self.broadcast_user_list()
        user = await get_player_by_id(user_id)
        user.online_status = 'Offline'
        user.save()

    async def receive(self, text_data):
        if not text_data:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )
        else:
            try:
                data = json.loads(text_data)
            except ValueError as e:
                # print(f"Invalid JSON: {e}")
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'group_room_list'
                    }
                )
                return
            # if text_data['message'] == "close":
            #     await self.close()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )
            if data.get('type') == 'update':
                await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )
            elif data.get('type') == 'authenticate':
                await self.authenticate(data['token'])
            elif data.get('type') == 'tournament-quit':
                await self.quit_tournament(data)
            elif data.get('type') == 'add_to_group':
                await self.add_owner_to_group(data)
            elif data.get('type') == 'status':
                await self.update_online_status(data)
            elif data.get('type') == 'friend_request_send':
                await self.send_friend_request(data)
            elif data.get('type') == 'friend_request_receive':
                await self.friend_request_receive(data)

    async def send_friend_request(self, data):
        await self.channel_layer.group_send(self.group_name,{'type': 'friend_request_receive', "sender": data.get('sender'), 'receiver': data.get('friend')})

    async def friend_request_receive(self, data):
        if self.login == data.get('receiver'):
            await self.send(text_data=json.dumps({'type': 'friend_request_receive', 'sender': data.get('sender'), 'receiver': data.get('receiver')}))


    async def update_online_status(self, data):
        user = await get_user_from_login(data.get('login'))
        if user:
            self.user = user
            self.user.online_status = 'Online'
            self.user.save()

    async def authenticate(self, token):
        user = await get_user_from_token(token)
        if user:
            self.user = user
            self.user_id = user.id
            self.login = user.login
            self.user.online_status = 'Online'
            self.user.save()
            unique_group_name = f"user_{self.user_id}"
            await self.channel_layer.group_add(unique_group_name, self.channel_name)
            RoomsConsumer.connected_users.add(self.user_id)
            await self.broadcast_user_list()
        else:
            await self.close(code=4001)
    
    async def close_connection(self, data):
        await self.send(text_data=json.dumps({
            "type": 'close',
            "login_id": data['login_id']
        }))
    
    async def quit_tournament(self, data):
        tourId = data.get('tour_id')
        tournament = await get_tournament(tourId)
        if tournament and self.user == tournament.owner:
            name = tournament.name
            url = f"http://blockchain:9000/delete_tournament/{name}"
            response = requests.get(url)
            response.raise_for_status()
            await database_sync_to_async(tournament.delete)()
        else:
            await self.send(text_data=json.dumps({"type": "error_nf"}))

    async def broadcast_user_list(self):
        connected_user_ids = list(RoomsConsumer.connected_users)
        players_list = await get_connected_players(connected_user_ids)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_users',
                'users': players_list,
            }
        )
    
    async def broadcast_users(self, event):
        await self.send(text_data=json.dumps({
            'type': 'users_list',
            'users': event['users'],
        }))

    async def group_room_list(self, event):
        rooms = RoomsModel.objects.filter(tournamentRoom=False)
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)

    async def send_message_to_user(self, user_id, message_type, content):
        unique_group_name = f"user_{user_id}"
        message = {
            'type': message_type,
            'message': content,
        }
        await self.channel_layer.group_send(
            unique_group_name,
            {
                'type': 'send_message',
                'text': json.dumps(message),
            }
        )
    
    async def send_message(self, event):
        message_content = json.loads(event['text'])
        await self.send(text_data=json.dumps(message_content))