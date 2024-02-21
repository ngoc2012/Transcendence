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
        if hasattr(self, 'user_id'):
            unique_group_name = f"user_{self.user_id}"
            await self.channel_layer.group_discard(unique_group_name, self.channel_name)
        user_id = getattr(self, 'user_id', None)
        if user_id in RoomsConsumer.connected_users:
            RoomsConsumer.connected_users.remove(user_id)
            await self.broadcast_user_list()

    async def receive(self, text_data):
        if not text_data:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )
        else:
            data = json.loads(text_data)
            if data.get('type') == 'update':
                await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'group_room_list'
                }
            )
            elif data.get('type') == 'authenticate':
                login = data.get('login')
                player = await get_player_by_login(login)
                if player:
                    self.user_id = player.id  # store the authenticated user's database ID in the instance of the consumer class
                    unique_group_name = f"user_{self.user_id}"
                    await self.channel_layer.group_add(unique_group_name, self.channel_name)  # add user to unique group
                    RoomsConsumer.connected_users.add(self.user_id) # class level
                    await self.broadcast_user_list()
                    await self.send(text_data=json.dumps({'message': 'Socket authentication successful'}))
                else:
                    await self.send(text_data=json.dumps({'message': 'Socket authentication failed'}))
                    await self.close(code=1008)
            elif data.get('type') == 'request_users_list':
                await self.broadcast_user_list()
            elif data.get('type') == 'tournament_invite':
                invitee_login = data.get('inviteeId')
                tour_id = data.get('tourId')
                invitee = await get_player_by_login(invitee_login)
                invitee_id = invitee.id
                if invitee_id in RoomsConsumer.connected_users:
                    print('invitee id found')
                    await self.send_invite_to_user(invitee_id, tour_id)

    async def send_invite_to_user(self, invitee_id, tour_id):
        invite_message = {
            'type': 'tournament_invite',
            'message': f'You have been invited to join tournament {tour_id}',
            'tour_id': tour_id,
        }
        # target the invitee socket 
        unique_group_name = f"user_{invitee_id}"
        await self.channel_layer.group_send(
            unique_group_name,
            {
                'type': 'send_tournament_invite',
                'text': json.dumps(invite_message),
            }
        )
    
    async def send_tournament_invite(self, event):
        # forward the event's data directly to the client
        await self.send(text_data=event["text"])


    async def broadcast_user_list(self):
        connected_user_ids = list(RoomsConsumer.connected_users)
        players_list = await get_connected_players_async(connected_user_ids)
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
        rooms = RoomsModel.objects.all()
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)
