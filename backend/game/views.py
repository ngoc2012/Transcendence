from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RoomsModel, TournamentMatchModel
from accounts.models import PlayersModel

import jwt
from pong.data import pong_data
import os
import json, random
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core.cache import cache

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

def get_data(game):
    if game == 'pong':
        return pong_data
    return {}

def add_player_to_room(game_id, login):
    if not RoomsModel.objects.filter(id=game_id).exists():
        return None, None
    room = RoomsModel.objects.get(id=game_id)

    if not PlayersModel.objects.filter(login=login).exists():
        return room, None
    player = PlayersModel.objects.get(login=login)

    k_team0 = str(room.id) + "_team0"
    k_team1 = str(room.id) + "_team1"
    k_players = str(room.id) + "_all"
    team0 = cache.get(k_team0)
    if team0 == None:
        team0 = []
    team1 = cache.get(k_team1)
    if team1 == None:
        team1 = []
    players = cache.get(k_players)
    if players == None:
        players = []
    n0 = len(team0)
    n1 = len(team1)
    if n1 >= n0:
        team0.append(player.id)
        cache.set(k_team0, team0)
        position = n0
    else:
        team1.append(player.id)
        cache.set(k_team1, team1)
        position = n1
    players.append(player.id)
    cache.set(k_players, players)
    if room.game == 'pong':
        k_player_x = str(room.id) + "_" + str(player.id) + "_x"
        k_player_y = str(room.id) + "_" + str(player.id) + "_y"
        player_x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
        cache.set(k_player_x, player_x)
        if player.id not in team0:
            cache.set(k_player_x, pong_data['WIDTH'] - player_x - pong_data['PADDLE_WIDTH'])
        cache.set(k_player_y, pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2)
    return room, player

def new_game(request):
    if 'game' not in request.POST:
        return (HttpResponse("Error: No game!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'name' not in request.POST:
        return (HttpResponse("Error: No name!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    room = RoomsModel(
        game=request.POST['game'],
        name=request.POST['name'],
    )
    room.save()
    if room.game == 'pong':
        cache.set(str(room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(str(room.id) + "_y", pong_data['HEIGHT'] / 2)
        room, player = add_player_to_room(room.id, request.POST['login'])
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))

def update(request):
    data = [
        {
            "id": str(i),
            "name": i.name
        } for i in RoomsModel.objects.all()
    ]
    # print(data)
    return JsonResponse(data, safe=False)

def join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    players = cache.get(str(request.POST['game_id']) + "_all")
    if players == None:
        players = []
    player = PlayersModel.objects.get(login=request.POST['login'])
    if player.id in players:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " is already in the room!"))
    room, player = add_player_to_room(request.POST['game_id'], request.POST['login'])
    if room == None:
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    if player == None:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " does not exist!"))
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))



def delete(request):
    if 'game_id' not in request.POST:
        return JsonResponse({'error': 'No game id!'}, status=400)
    if 'login' not in request.POST:
        return JsonResponse({'error': 'No login!'}, status=400)

    try:
        player = PlayersModel.objects.get(login=request.POST['login'])
    except PlayersModel.DoesNotExist:
        return JsonResponse({'error': "Login '{}' does not exist!".format(request.POST['login'])}, status=404)

    try:
        room = RoomsModel.objects.get(id=request.POST['game_id'])
    except RoomsModel.DoesNotExist:
        return JsonResponse({'error': "Room with id '{}' does not exist!".format(request.POST['game_id'])}, status=404)

    s = "Room {} - {} deleted".format(room.name, room)

    if room.owner != player:
        return JsonResponse({'error': "Login '{}' is not the owner of '{}'!".format(request.POST['login'], request.POST['game_id'])}, status=401)

    # if PlayerRoomModel.objects.filter(room=room.id).count() > 0:
    #     return JsonResponse({'error': "Someone is still playing"}, status=401)

def tournament_join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    room, player = add_player_to_room(request.POST['game_id'], request.POST['login'])
    if room == None:
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    if player == None:
        return (HttpResponse("Error: Player with id " + request.user.id + " does not exist!"))
    match = TournamentMatchModel.objects.filter(room=room).first()
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))

@require_POST
def tournament_local_join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    room = RoomsModel.objects.get(id=request.POST['game_id'])
    player = PlayersModel.objects.get(id=room.owner.id)
    match = TournamentMatchModel.objects.filter(room=room).first()
    # if not room.server:
    #     room.server = player
    #     room.save()
    #     side = 0
    #     position = 0
    # else:
    # side = 0
    # position = 0
    # player_room = PlayerRoomModel.objects.create(
    # player=player,
    # room=room,
    # side=side,
    # position=position)
    # # player_room = PlayerRoomModel.objects.get(player=player)
    # if room.game == 'pong':
    #     player_room.x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
    #     if side == 1:
    #         player_room.x = pong_data['WIDTH'] - player_room.x - pong_data['PADDLE_WIDTH']
    #     player_room.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
    # player_room.save()
    # player.save()
    
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))

def tournament_local_results(tournament):
    return

def tournament_local_get(request):
    if request.method == 'POST':
        try:
            tour_id = request.POST["id"]
            tournament = TournamentModel.objects.get(id=tour_id)
            participants = tournament.participantsLocal

            if len(participants) == 1:
                tournament.terminated = True
                return tournament_local_results(tournament)
            elif len(participants) == 2:
                tournament.final = True
            elif len(participants) % 2 != 0:
                random_participant = random.choice(participants)
                tournament.participantsLocal.remove(random_participant)
                tournament.waitlistLocal.add(random_participant)
            tournament.save()

            if tournament.localMatchIP:
                last_match = TournamentMatchModel.objects.filter(tournament=tournament).order_by('-id').first()
                return JsonResponse({
                    'name': tournament.name,
                    'round': tournament.round,
                    'match': tournament.total_matches,
                    'player1': last_match.player1Local,
                    'player2': last_match.player2Local,
                    'room_id': str(last_match.room_uuid),
                })

            random.shuffle(participants)
            i = 0;
            player1 = participants[i]
            player2  = participants[i + 1]
            room = RoomsModel.objects.create(
                game=tournament.game,
                name=f"{tournament.name} - Match {tournament.total_matches}",
                owner=tournament.owner,
                server=tournament.owner,
                tournamentRoom=True
            )
            if room.game == 'pong':
                room.x = pong_data['PADDLE_WIDTH'] + pong_data['RADIUS']
                room.y = pong_data['HEIGHT'] / 2
                room.save()
            match = TournamentMatchModel.objects.create(
                tournament=tournament,
                room=room,
                room_uuid=room.id,
                player1Local=player1,
                player2Local=player2,
                start_time=timezone.now(),
                round_number=tournament.round,
                match_number=tournament.total_matches)
            tournament.active_matches += 1
            tournament.total_matches += 1 
            tournament.localMatchIP = True
            tournament.participantsLocal.remove(player1)
            tournament.participantsLocal.remove(player2)
            tournament.waitlistLocal.append(player1)
            tournament.waitlistLocal.append(player2)
            tournament.save()
            if player1 and player2:
                return JsonResponse({
                    'name': tournament.name,
                    'round': tournament.round,
                    'match': tournament.total_matches,
                    'player1': player1,
                    'player2': player2,
                    'room_id': str(room.id),
                })
        except:
            return JsonResponse({'error'})
    else:
        return JsonResponse({'error': 'This endpoint only accepts POST requests.'}, status=405)
    

def tournament_local_verify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            players = data.get('players')
            if not players:
                return JsonResponse({'error': 'Missing players'}, status=400)

            User = get_user_model()
            for player in players:
                try:
                    user = User.objects.get(username=player)
                    return JsonResponse({'error': f'Player {player} already exists'}, status=400)
                except User.DoesNotExist:
                    continue

            if not len(players) == len(set(players)):
                return JsonResponse({'error': 'Players can not have the same name'}, status=400)
                      
            tour_id = data.get('id')
            tournament = TournamentModel.objects.get(id=tour_id)
            if tournament:
                for player in players:
                    tournament.participantsLocal.append(player)
                tournament.save()
            else:
                return JsonResponse({'error': 'Tournament not found'}, status=400)       
            
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Error decoding JSON: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        return JsonResponse({'message': 'Done'})
    else:
        return JsonResponse({'error': 'This endpoint only accepts POST requests.'}, status=405)

# from channels.layers import get_channel_layer
from backend.asgi import channel_layer
from asgiref.sync import async_to_sync
def close_connection(request, login_id):
    async_to_sync(channel_layer.group_send)(
        "rooms",
        {
            'type': 'close_connection',
            'login_id': login_id
        }
    )
    return HttpResponse("done")

def need_update(request):
    async_to_sync(channel_layer.group_send)(
        "rooms",
        {
            'type': 'group_room_list',
        }
    )
    return HttpResponse("done")
