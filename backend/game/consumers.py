import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import RoomsModel, PlayersModel, TournamentModel, TournamentMatchModel, PlayerRoomModel
from pong.data import pong_data
from django.utils import timezone

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
def get_tournament(tour_id):
    try:
        return TournamentModel.objects.get(id=tour_id)
    except TournamentModel.DoesNotExist:
        return None
    
@database_sync_to_async
def get_match(match_id):
    try:
        return TournamentMatchModel.objects.get(id=match_id)
    except TournamentMatchModel.DoesNotExist:
        return None

@database_sync_to_async
def get_tournament_participants(tournament):
    return list(tournament.participants.all())

@database_sync_to_async  
def new_room(i, tournament):
            room = RoomsModel.objects.create(
                game=tournament.game,
                name=f"{tournament.name} - Match {i}",
                owner=tournament.owner,
                server=tournament.owner
            )
            if room.game == 'pong':
                room.x = pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
                room.y = pong_data['HEIGHT'] / 2
                room.save()
            player_room = PlayerRoomModel.objects.create(
                player=tournament.owner,
                room=room,
                side=0,
                position=0
            )
            if room.game == 'pong':
                player_room.x = 0
                player_room.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
                player_room.save()
            
            return room

@database_sync_to_async      
def create_tournament_match(tournament, room, player1, player2, round_number):
    return TournamentMatchModel.objects.create(
        tournament=tournament,
        room=room,
        player1=player1,
        player2=player2,
        round_number=round_number,
        start_time=timezone.now()
    )

@database_sync_to_async  
def odd_participants_adjust(tournament, last_participant):
    tournament.participants.remove(last_participant)
    tournament.waitlist.add(last_participant)
    
@database_sync_to_async
def get_tournament_owner(tour_id):
    tournament = TournamentModel.objects.filter(id=tour_id).first()
    if tournament:
        organizer_id = tournament.owner.id
        return organizer_id
    return None

@database_sync_to_async
def get_matches_by_status(tournament_id, status):
    return list(TournamentMatchModel.objects.filter(
        tournament_id=tournament_id, 
        status=status
    ).select_related('room', 'player1', 'player2'))


get_connected_players_async = database_sync_to_async(get_connected_players)

class RoomsConsumer(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
        # user = self.scope['user']
    
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
        print(text_data)
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
                print(f"Invalid JSON: {e}")
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'group_room_list'
                    }
                )
                return
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
            elif data.get('type') == 'tournament_invite':
                await self.process_tournament_invite(data)
            elif data.get('type') == 'tournament_invite_resp':
                await self.process_tournament_invite_response(data)
            elif data.get('type') == 'tournament_rounds':
                await self.handle_tournament_round(data)
            elif data.get('type') == 'tournament-player-action':
                await self.handle_tournament_player(data)
            elif data.get('type') == 'tournament-join':
                await self.handle_tournament_join(data)
            elif data.get('type') == 'tournament_event_invite':
                await self.handle_tourevent_invite(data)
            elif data.get('type') == 'tournament_list':
                await self.handle_tour_matches(data)

    async def handle_tourevent_invite(self, data):
        tour_id = data.get('tour_id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'Tournament not found'}))
            return
        
        participants = await get_tournament_participants(tournament)
        for participant in participants:
            if participant.id != self.user_id:
                await self.send_message_to_user(participant.id, 'tournament_event_invite', str(tour_id))

    async def handle_tournament_join(self, data):
        tour_id = data.get('tour_id')
        match_id = data.get('match_id')
        tournament = await get_tournament(tour_id)
        # if not tournament:
        #     await self.send(text_data=json.dumps({'error': 'Tournament not found'}))
        #     return
        # match = await database_sync_to_async(TournamentMatchModel.objects.select_related('tournament').get)(id=match_id)
        # if not match:
        #     await self.send(text_data=json.dumps({'error': 'Match not found'}))
        #     return
        # if match.tournament.id != tournament.id:
        #     await self.send(text_data=json.dumps({'error': 'Match does not belong to tournament'}))
        #     return
        await self.send(text_data=json.dumps({
            'type': 'tournament_join_valid',
            'tourId': str(tournament.id),
            'matchId': str(match_id)
        }))

    async def handle_tournament_player(self, data):
        id = data.get('id')
        tournament = await get_tournament(id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'Tournament not found'}))
            return
        
        participant_ids = await sync_to_async(list)(tournament.participants.values_list('id', flat=True))
        if self.user_id in participant_ids:
            room_id = await self.get_user_match_room_id(id)
            if room_id:
                await self.send_message_to_user(self.user_id, 'tournament_join', str(room_id))

    async def handle_tournament_round(self, data):
        tour_id = data.get('id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'Tournament not found'}))
            return

        participants = await get_tournament_participants(tournament)

        if len(participants) % 2 != 0:
            last_participant = participants[-1]
            await odd_participants_adjust(tournament, last_participant)

        for i in range(0, len(participants), 2):
            player1 = participants[i]
            player2 = participants[i + 1] if i + 1 < len(participants) else None
            if player1 and player2:
                room = await new_room(i // 2, tournament)
                match = await create_tournament_match(tournament, room, player1, player2, tournament.round)
                
    async def handle_tour_matches(self, data):
        tour_id = data.get('id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'Tournament not found'}))
            return
        
        await self.send(text_data=json.dumps({
            'type': 'tournament_infos',
            'name': tournament.name,
            'round': tournament.round
        }))
        
        matches = await get_matches_by_status(tour_id, 'Waiting for players to join')
        
        matches_data = [{
        'room_id': str(match.room.id),
        'player1_name': match.player1.name,
        'player2_name': match.player2.name if match.player2 else 'Awaiting player',
        'status': match.status
        } for match in matches]

        await self.send(text_data=json.dumps({
            'type': 'tournament_matches',
            'matches': matches_data,
        }))

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

    async def get_user_match_room_id(self, tour_id):
        match = await database_sync_to_async(
            TournamentMatchModel.objects.filter(
                tournament_id=tour_id, 
                player1__id=self.user_id  # player1__id: query foreign key relations
            ).first
        )()

        if not match:
            match = await database_sync_to_async(
                TournamentMatchModel.objects.filter(
                    tournament_id=tour_id, 
                    player2__id=self.user_id
                ).first
            )()

        if match:
            room = await database_sync_to_async(lambda: match.room)()
            return room.id

        return None