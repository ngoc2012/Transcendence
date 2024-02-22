import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import RoomsModel, PlayersModel, TournamentModel

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

@database_sync_to_async
def add_player_to_tournament(player_id, tour_id):
    try:
        tournament = TournamentModel.objects.get(id=tour_id)
        player = PlayersModel.objects.get(id=player_id)
        tournament.participants.add(player)
        return True, {"participants_count": tournament.participants.count()}
    except (TournamentModel.DoesNotExist, PlayersModel.DoesNotExist):
        return False, {}
    
@database_sync_to_async
def get_tournament_owner(tour_id):
    tournament = TournamentModel.objects.filter(id=tour_id).first()
    if tournament:
        organizer_id = tournament.owner.id
        return organizer_id
    return None

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
                    await self.channel_layer.group_add(unique_group_name, self.channel_name)  # add user to unique group for one-o-one communication
                    RoomsConsumer.connected_users.add(self.user_id) # class level
                    await self.broadcast_user_list()
                    await self.send(text_data=json.dumps({'message': 'Socket authentication successful'}))
                else:
                    await self.send(text_data=json.dumps({'message': 'Socket authentication failed'}))
                    await self.close(code=1008)
            elif data.get('type') == 'request_users_list':
                await self.broadcast_user_list()
            elif data.get('type') == 'tournament_invite' or data.get('type') == 'tournament_invite_resp':
                await self.handle_tournament_invitation(data)
            
    async def handle_tournament_invitation(self, data):
        if data.get('type') == 'tournament_invite':
            await self.process_tournament_invite(data)
        elif data.get('type') == 'tournament_invite_resp':
            await self.process_tournament_invite_response(data)

    async def process_tournament_invite(self, data):
        invitee_login_id = data.get('inviteeId')
        tournament_id = data.get('tourId')
        invitee = await get_player_by_login(invitee_login_id)
        if invitee and invitee.id in RoomsConsumer.connected_users:
            await self.send_message_to_user(invitee.id, 'tournament_invite', tournament_id)

    async def process_tournament_invite_response(self, data):
        response = data.get('response')
        tournament_id = data.get('id')
        login = data.get('login')
        if response == 'accept':
            success, info_dict = await add_player_to_tournament(self.user_id, tournament_id)
            if success:
                owner_id = await get_tournament_owner(tournament_id)
                if owner_id:
                    await self.send_message_to_user(owner_id, 'tournament_invite_accepted', login)
                if info_dict.get('participants_count', 0) >= 2:
                    await self.send_message_to_user(owner_id, 'tournament_ready', 'tournamentOK')


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
