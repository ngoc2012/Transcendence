import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import RoomsModel, PlayersModel

@sync_to_async
def room_list(rooms):
    return json.dumps([
        {
            "id": str(i),
            "name": i.name
            } for i in rooms])

@database_sync_to_async
def get_player_by_login(login):
    return PlayersModel.objects.filter(login=login).first()

def get_connected_players(connected_user_ids):
    return list(PlayersModel.objects.filter(id__in=connected_user_ids).values('id', 'login', 'name'))


get_connected_players_async = database_sync_to_async(get_connected_players)

class RoomsConsumer(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
        user = self.scope['user']
    
        self.group_name = "rooms"
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
        user_id = getattr(self, 'user_id', None)
        if user_id in RoomsConsumer.connected_users:
            RoomsConsumer.connected_users.remove(user_id)
            await self.broadcast_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'authenticate':
            login = data.get('login')
            player = await get_player_by_login(login)
            if player:
                self.user_id = player.id  # Store the authenticated user's database ID in the instance of the consumer class
                RoomsConsumer.connected_users.add(self.user_id)
                await self.broadcast_user_list()
                await self.send(text_data=json.dumps({'message': 'Socket authentication successful'}))
            else:
                await self.send(text_data=json.dumps({'message': 'Socket authentication failed'}))
                await self.close(code=1008)

        if data.get('type') == 'request_users_list':
            connected_user_ids = list(RoomsConsumer.connected_users)
            players_list = await get_connected_players_async(connected_user_ids)
            await self.send(text_data=json.dumps({
                'type': 'users_list',
                'users': players_list,
            }))

        else:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )

    async def broadcast_user_list(self):
        connected_user_ids = list(RoomsConsumer.connected_users)
        players_list = await get_connected_players_async(connected_user_ids)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_users',  # method
                'users': players_list,
            }
        )
    
    async def broadcast_users(self, event):
        await self.send(text_data=json.dumps({
            'type': 'users_list',
            'users': event['users'],
        }))


    
    async def group_room_list(self, event):
        rooms = RoomsModel.objects.all()
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)
