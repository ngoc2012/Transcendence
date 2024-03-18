import json, random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import RoomsModel, PlayersModel, TournamentModel, TournamentMatchModel, PlayerRoomModel
from pong.data import pong_data
from django.utils import timezone
from django.db.models import Q

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
def get_room_by_id(roomId):
    return RoomsModel.objects.filter(id=roomId).first()

@database_sync_to_async
def get_match_by_room(room):
    return TournamentMatchModel.objects.filter(room=room).select_related('tournament', 'player1', 'player2').first()

def get_connected_players(connected_user_ids):
    return list(PlayersModel.objects.filter(id__in=connected_user_ids).values('id', 'login', 'name'))

@database_sync_to_async
def get_tournament(tour_id):
    try:
        return TournamentModel.objects.select_related('owner', 'winner').get(id=tour_id)
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
def get_tournament_players(tournament):
    participants = tournament.participants.all()
    waitlist = tournament.waitlist.all()
    combined_list = list(participants) + list(waitlist)
    return combined_list

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

@database_sync_to_async
def get_round_matches(tournament_id):
    tournament = TournamentModel.objects.get(id=tournament_id)
    return list(TournamentMatchModel.objects.filter(
        tournament_id=tournament_id,
        round_number=tournament.round
        # winner__isnull=True
    ).select_related('room', 'player1', 'player2'))

@database_sync_to_async
def get_all_tournament_matches(tournament_id):
    return list(TournamentMatchModel.objects.filter(tournament__id=tournament_id).select_related('player1', 'player2', 'winner', 'room'))
    
get_connected_players_async = database_sync_to_async(get_connected_players)

@database_sync_to_async
def new_room(i, tournament, player1, player2):
    room = RoomsModel.objects.create(
        game=tournament.game,
        name=f"{tournament.name} - Match {i}",
        owner=player1,
        # server=player1,
        tournamentRoom=True
    )
    if room.game == 'pong':
        room.x = pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
        room.y = pong_data['HEIGHT'] / 2
        room.save()
    return room

@database_sync_to_async      
def create_tournament_match(tournament, room, player1, player2, round_number):
    tournament.active_matches += 1
    tournament.total_matches += 1
    tournament.save()
    return TournamentMatchModel.objects.create(
        tournament=tournament,
        room=room,
        room_uuid=room.id,
        player1=player1,
        player2=player2,
        round_number=round_number,
        match_number=tournament.total_matches,
        start_time=timezone.now()
    )

@database_sync_to_async  
def odd_participants_adjust(tournament, last_participant):
    tournament.participants.remove(last_participant)
    tournament.waitlist.add(last_participant)

@database_sync_to_async
def add_loser_to_eleminated(tournament, loser):
    tournament.participants.remove(loser)
    tournament.eliminated.add(loser)

@database_sync_to_async
def clear_waitlist(tournament):
    waitlist_players = tournament.waitlist.all()
    for player in waitlist_players:
        tournament.participants.add(player)
        tournament.waitlist.remove(player)


@database_sync_to_async
def check_player_in_tournament(player):
    tournament = TournamentModel.objects.filter(
        (Q(participants=player) | 
        Q(waitlist=player) | 
        Q(eliminated=player)) &
        Q(terminated=False)).distinct().first()
    return tournament

@database_sync_to_async
def get_winner(tournament):
    return tournament.participants.first()

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
            elif data.get('type') == 'tournament_registered':
                await self.handle_tournament_registered(data)
            elif data.get('type') == 'tournament_creation_request':
                await self.check_user_in_tournament(data)
            elif data.get('type') == 'match_start':
                await self.update_match_status(data, 'In Progress')
            elif data.get('type') == 'match_result':
                await self.update_match_result(data)
            elif data.get('type') == 'tournament-quit':
                await self.quit_tournament(data)
            elif data.get('type') == 'tournament-info-request':
                await self.tour_info_request(data)
    
    async def close_connection(self, data):
        await self.send(text_data=json.dumps({
            "type": 'close',
            "login_id": data['login_id']
        }))

    async def tour_info_request(self, data):
        tourID = data.get('id')
        tournament = await get_tournament(tourID)
        if (tournament):
            await self.tournament_info_update(tournament)
    
    async def quit_tournament(self, data):
        tourId = data.get('tour_id')
        tournament = await get_tournament(tourId)
        if (tournament):
            await database_sync_to_async(tournament.delete)()

    async def update_match_result(self, data):
        roomId = data.get('roomid')
        winnerPlc = data.get('winner')
        room = await get_room_by_id(roomId)
        if not room:
            return
        match = await get_match_by_room(room)
        if not match:
            return
        if not match.end_time:
            match.end_time = timezone.now()
            if winnerPlc == 'player0':
                match.winner = match.player1
                match.loser = match.player2
            else:
                match.winner = match.player2
                match.loser = match.player1
            match_winner_login = match.winner.login
            match.status = f"Terminated - Winner: {match_winner_login}"
            match.p1_score = data.get('score')[0]
            match.p2_score = data.get('score')[1]
            tournament = match.tournament
            await add_loser_to_eleminated(tournament, match.loser)
            await database_sync_to_async(match.save)()
            data_status = {'roomId': roomId}
            await self.update_match_status(data_status, match.status)
            tournament.active_matches -= 1
            await database_sync_to_async(tournament.save)()
            await self.update_players_elo(match)
            if tournament.active_matches == 0:
                await clear_waitlist(tournament)
                tournament.round = tournament.round + 1
                await database_sync_to_async(tournament.save)()
                data = {'id': tournament.id}
                await self.handle_tournament_round(data)
                tourIdData = {'tour_id': tournament.id}
                await self.handle_tourevent_invite(tourIdData)
            await self.update_lobby_status(tournament)

    async def update_players_elo(this, match):
        player1 = match.player1
        player2 = match.player2
        player1_expected_score = 1 / (1 + 10 ** ((player2.elo - player1.elo) / 400))
        player2_expected_score = 1 / (1 + 10 ** ((player1.elo - player2.elo) / 400))
        if match.winner == match.player1:
            player1_new_elo = player1.elo + 16 * (1 - player1_expected_score)
            player2_new_elo = player2.elo + 16 * (0 - player2_expected_score)
        else:
            player2_new_elo = player2.elo + 16 * (1 - player2_expected_score)
            player1_new_elo = player1.elo + 16 * (0 - player1_expected_score)
        player1.elo = round(player1_new_elo)
        player2.elo = round(player2_new_elo)
        await database_sync_to_async(player1.save)()
        await database_sync_to_async(player2.save)()

    async def tournament_info_update(self, tournament):
        channel_layer = get_channel_layer()
        group_name = f"tournament_{tournament.id}"

        if tournament.terminated == True:
            message = {
                'type': 'tournament_infos',
                'data': {
                    'name': tournament.name,
                    'round': -2
                }
            }
        elif tournament.final == True:
            message = {
                'type': 'tournament_infos',
                'data': {
                    'name': tournament.name,
                    'round': -1
                }
            }
        else:
            message = {
                'type': 'tournament_infos',
                'data': {
                    'name': tournament.name,
                    'round': tournament.round
                }
            }
        await channel_layer.group_send(group_name,
            {
                'type': 'send_tournament_info',
                'message': message
            }
        )

    async def update_lobby_status(self, tournament):
        matches = await get_all_tournament_matches(tournament.id)
        channel_layer = get_channel_layer()
        await self.tournament_info_update(tournament)

        if not matches:
            return      
        matches_data = [{
            'room_id': str(match.room_uuid),
            'match_nbr': match.match_number,
            'player1_name': match.player1.name,
            'player2_name': match.player2.name if match.player2 else 'Awaiting player',
            'status': match.status,
            'round': match.round_number
        } for match in matches]

        group_name = f"tournament_{tournament.id}"
        message = {
        'type': 'match_status_update',
        'data': {
            'type': 'match_update',
            'matches': matches_data,
            }
        }
        await channel_layer.group_send(group_name, message)

    async def update_match_status(self, data, text):
        roomId = data.get('roomId')
        room = await get_room_by_id(roomId)
        if not room:
            return
        match = await get_match_by_room(room)
        if not match:
            return
        match.start_time = timezone.now()
        match.status = text
        await database_sync_to_async(match.save)()
        group_name = f"tournament_{match.tournament_id}"
        message = {
        'type': 'match_status_update',
        'data': {
            'type': 'match_status_update',
            'match_nbr': match.match_number,
            'room_id': roomId,
            'status': match.status,
            }
        }
        channel_layer = get_channel_layer()
        await channel_layer.group_send(group_name, message)

    async def match_status_update(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))

    async def check_user_in_tournament(self, data):
        login = data.get('login')
        user = await get_player_by_login(login)
        if user:
            tournament = await check_player_in_tournament(user)
            if tournament:
                await self.send_message_to_user(user.id, 'already_in_tournament', str(tournament.id))
                return
            await self.send_message_to_user(user.id, 'tournament_creation_OK', login)

    async def handle_tournament_registered(self, data):
        login = data.get('login')
        user = await get_player_by_login(login)
        if user:
            tournament = await check_player_in_tournament(user)
            if tournament:
                await self.send_message_to_user(self.user_id, 'tournament_in_progress', str(tournament.id))

    async def handle_tourevent_invite(self, data):
        tour_id = data.get('tour_id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'handle_tourevent_invite Tournament not found'}))
            return
    
        participants = await get_tournament_players(tournament)
        for participant in participants:
            if participant.id != self.user_id:
                await self.send_message_to_user(participant.id, 'tournament_event_invite', str(tour_id))

    async def handle_tournament_join(self, data):
        tour_id = data.get('tour_id')
        match_id = data.get('match_id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'handle_tournament_join Tournament not found'}))
            return
        match = await database_sync_to_async(TournamentMatchModel.objects.select_related('tournament').get)(room=match_id)
        if not match:
            await self.send(text_data=json.dumps({'error': 'Match not found'}))
            return
        await self.send(text_data=json.dumps({
            'type': 'tournament_join_valid',
            'tourId': str(tournament.id),
            'matchId': str(match_id)
        }))

    async def handle_tournament_player(self, data):
        id = data.get('id')
        tournament = await get_tournament(id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'handle_tournament_player Tournament not found'}))
            return
        
        participant_ids = await sync_to_async(list)(tournament.participants.values_list('id', flat=True))
        waitlist_ids = await sync_to_async(list)(tournament.waitlist.values_list('id', flat=True))
        combined_ids = participant_ids + waitlist_ids
        if self.user_id in combined_ids:
            room_id = await self.get_user_match_room_id(id)
            if room_id:
                await self.send_message_to_user(self.user_id, 'tournament_join', str(room_id))

    async def handle_tournament_round(self, data):
        tour_id = data.get('id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'handle_tournament_round Tournament not found'}))
            return

        participants = await get_tournament_participants(tournament)
        
        if len(participants) == 1:
            tournament.terminated = True
            winner = await get_winner(tournament)
            if winner:
                tournament.winner = winner
            await database_sync_to_async(tournament.save)()
            return
        elif len(participants) == 2:
            tournament.final = True
            await database_sync_to_async(tournament.save)()
        elif len(participants) % 2 != 0:
            random_participant = random.choice(participants)
            await odd_participants_adjust(tournament, random_participant)
            participants = await get_tournament_participants(tournament)

        participants.sort(key=lambda participant: participant.elo, reverse=True)
        for i in range(0, len(participants), 2):
            player1 = participants[i]
            player2 = participants[i + 1] if i + 1 < len(participants) else None
            if player1 and player2:
                room = await new_room(i // 2, tournament, player1, player2)
                match = await create_tournament_match(tournament, room, player1, player2, tournament.round)
                
    async def handle_tour_matches(self, data):
        tour_id = data.get('id')
        tournament = await get_tournament(tour_id)
        if not tournament:
            await self.send(text_data=json.dumps({'error': 'handle_tour_matches : Tournament not found'}))
            return

        await self.tournament_info_update(tournament)

        if tournament.terminated == True:
            await self.send(text_data=json.dumps({
                'type': 'tournament_winner',
                'winner': tournament.winner.login,
            }))

            # score history
            tournament_matches = await get_all_tournament_matches(tournament.id)

            matches_data = []
            for match in tournament_matches:
                match_info = {
                    'round_number': match.round_number,
                    'player1_login': match.player1.login,
                    'player2_login': match.player2.login,
                    'player1_score': match.p1_score,
                    'player2_score': match.p2_score,
                    'winner_login': match.winner.login if match.winner else 'No winner yet',
                }
                matches_data.append(match_info)

            await self.send(text_data=json.dumps({
                'type': 'all_tournament_matches',
                'matches': matches_data,
            }))

        else:
            matches = await get_all_tournament_matches(tournament.id)
            
            matches_data = [{
                'room_id': str(match.room_uuid),
                'match_nbr': match.match_number,
                'player1_name': match.player1.login,
                'player2_name': match.player2.login,
                'status': match.status,
                'round' : match.round_number
            } for match in matches]

            await self.send(text_data=json.dumps({
                'type': 'tournament_matches',
                'matches': matches_data,
            }))
        
    async def process_tournament_invite(self, data):
        invitee_login_id = data.get('inviteeId')
        tournament_id = data.get('tourId')
        tournament = await get_tournament(tournament_id)
        owner_login = tournament.owner.login

        group_name = f"tournament_{tournament_id}"
        await self.channel_layer.group_add(group_name, self.channel_name)

        invitee = await get_player_by_login(invitee_login_id)
        content = {
            'message': f"You are invited to join {owner_login}'s tournament: '{tournament.name}'",
            'tour_id': tournament_id
        }
        if invitee and invitee.id in RoomsConsumer.connected_users:
            await self.send_message_to_user(invitee.id, 'tournament_invite', content)

    async def process_tournament_invite_response(self, data):
        response = data.get('response')
        tournament_id = data.get('id')
        login = data.get('login')
        user = await get_player_by_login(login)
        if response == 'accept':
            tournament_check = await check_player_in_tournament(user)
            if tournament_check:
                await self.send_message_to_user(user.id, 'already_in_tournament', login)
                return
            success, info_dict = await add_player_to_tournament(self.user_id, tournament_id)
            if success:
                group_name = f"tournament_{tournament_id}"
                await self.channel_layer.group_add(group_name, self.channel_name)
                owner_id = await get_tournament_owner(tournament_id)
                if owner_id:
                    await self.send_message_to_user(owner_id, 'tournament_invite_accepted', login)
                if info_dict.get('participants_count', 0) >= 3:
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
        rooms = RoomsModel.objects.filter(tournamentRoom=False)
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)


    async def get_user_match_room_id(self, tour_id):
        tournament = await get_tournament(tour_id)
        if not tournament or tournament.terminated:
            return None
        match = await database_sync_to_async(
            TournamentMatchModel.objects.filter(
                tournament_id=tour_id, 
                round_number = tournament.round,
                player1__id=self.user_id,
                winner=None
            ).first
        )()

        if not match:
            match = await database_sync_to_async(
                TournamentMatchModel.objects.filter(
                    tournament_id=tour_id, 
                    round_number = tournament.round,
                    player2__id=self.user_id,
                    winner=None
                ).first
            )()

        if match:
            room = await database_sync_to_async(lambda: match.room)()
            return room.id

        return None
    
    async def send_tournament_info(self, event):
        message_content = event['message']['data']
        
        formatted_message = {
            'type': event['message']['type'],
            'name': message_content['name'],
            'round': message_content['round']
        }
        await self.send(text_data=json.dumps(formatted_message))