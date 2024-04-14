from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RoomsModel, TournamentMatchModel, TournamentModel
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
from django.utils import timezone


JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

User = get_user_model()

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

def tournament_local_join_setup(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'player2' not in request.POST:
        return (HttpResponse("Error: No player id!"))
    player2 = request.POST["player2"]
    players = cache.get(str(request.POST['game_id']) + "_all")
    if players == None:
        players = []
    match = TournamentMatchModel.objects.get(room_uuid=request.POST["game_id"])
    player = PlayersModel.objects.get(login=player2)
    if not player:
        player = PlayersModel.objects.get(login='localTournament2')
    if player and player.id in players:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " is already in the room!"))
    room, player = add_player_to_room(request.POST['game_id'], player.login)
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
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))

def refresh_participants(tournament):
    tournament.participants.add(*list(tournament.waitlist.all()))
    tournament.waitlist.clear()

    if tournament.waitlistLocal:
        tournament.participantsLocal.extend(tournament.waitlistLocal)
        tournament.waitlistLocal = []

    tournament.save()


@require_POST
def tournament_local_result(request):
    try:
        room_id = request.POST.get("room")
        score1 = request.POST.get("score1")
        score2 = request.POST.get("score2")

        print(room_id)
        print(score1)
        print(score2)

        match = TournamentMatchModel.objects.get(room_uuid=room_id)

        match.end_time = timezone.now()
        match.p1_score = score1
        match.p2_score = score2
    
        if score1 > score2:
            if match.player1isLocal:
                match.winnerLocal = match.player1Local 
            else:
                match.winner = match.player1
            if match.player2isLocal:
                match.winnerLocal = match.player2Local
            else:
                match.winner = match.player2
        else:
            if match.player2isLocal:
                match.winnerLocal = match.player2Local
            else:
                match.winner = match.player2
        match.save()

        tournament = match.tournament
        if score1 > score2:
            if match.player2isLocal:
                tournament.eliminatedLocal.append(match.player2Local)
                tournament.waitlistLocal.remove(match.player2Local)
            else:
                tournament.eliminated.add(match.player2)
                tournament.waitlist.remove(match.player2)
        else:
            if match.player1isLocal:
                tournament.eliminatedLocal.append(match.player1Local)
                tournament.waitlistLocal.remove(match.player1Local)
            else:
                tournament.eliminated.add(match.player1)
                tournament.waitlist.remove(match.player1)

        tournament.localMatchIP = False
        tournament.active_matches -= 1
        if tournament.active_matches == 0:
            tournament.round += 1
            tournament.newRound = True
            refresh_participants(tournament)
        tournament.save()

        return JsonResponse({'status': 'ok'})
    except ValueError:
        return JsonResponse({'error': 'Invalid input for scores. Please provide numeric values.'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Room or match not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred: {}'.format(str(e))}, status=500)

@require_POST
def tournament_local_get(request):
    try:
        tour_id = request.POST["id"]
        tournament = TournamentModel.objects.get(id=tour_id)
        participants = list(tournament.participants.all())
        waitlist = list(tournament.waitlist.all())
        all_participants = tournament.participantsLocal
        all_waitlist = tournament.participantsLocal

        all_participants = list(tournament.participantsLocal if tournament.participantsLocal else [])
        all_waitlist = list(tournament.waitlistLocal if tournament.waitlistLocal else [])
        all_participants.extend(user.login for user in participants)
        all_waitlist.extend(user.login for user in waitlist)

        all_participants = list(set(all_participants))
        all_waitlist = list(set(all_waitlist))
        
        print('participants:', participants)
        print('waitlist:', waitlist)
        print('all participants:', all_participants)
        print('all waitlist:', all_waitlist)

        if len(all_participants) == 1 and not all_waitlist:
            tournament.terminated = True
            tournament.save()
            return tournament_local_end(tournament)
        elif len(all_participants) == 2 and not all_waitlist:
            tournament.final = True
        elif tournament.newRound:
            if len(all_participants) % 2 != 0:
                random_participant = random.choice(all_participants)
                move_player_to_waitlist(tournament, random_participant)
            tournament.newRound = False
        tournament.save()

        if tournament.localMatchIP:
            last_match = TournamentMatchModel.objects.filter(tournament=tournament).order_by('-id').first()
            return JsonResponse({
                'name': tournament.name,
                'round': tournament.round if tournament.final == False else 'final',
                'match': tournament.total_matches,
                'player1': last_match.player1Local if last_match.player1isLocal else last_match.player1.username,
                'player2': last_match.player2Local if last_match.player2isLocal else last_match.player2.username,
                'room_id': str(last_match.room_uuid),
            })

        tournament.total_matches += 1
        tournament.active_matches += 1
        random.shuffle(all_participants)
        player1 = all_participants[0]
        player2  = all_participants[1]

        print(player1)
        print(player2)
        room = RoomsModel.objects.create(
            game=tournament.game,
            name=f"{tournament.name} - Match {tournament.total_matches}",
            owner=tournament.owner,
            tournamentRoom=True
        )
        if room.game == 'pong':
            cache.set(str(room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
            cache.set(str(room.id) + "_y", pong_data['HEIGHT'] / 2)
            if player1 in tournament.participantsLocal:
                room, player = add_player_to_room(room.id, User.objects.get(login='localTournament1'))
            else:
                room, player = add_player_to_room(room.id, User.objects.get(login=player1))

        if player1 in tournament.participantsLocal and player2 in tournament.participantsLocal:
            match = TournamentMatchModel.objects.create(
                tournament=tournament,
                room=room,
                room_uuid=room.id,
                player1Local=player1,
                player2Local=player2,
                start_time=timezone.now(),
                round_number=tournament.round,
                match_number=tournament.total_matches,
                player1isLocal=True,
                player2isLocal=True)
        elif player1 in tournament.participantsLocal and player2 not in tournament.participantsLocal:
            match = TournamentMatchModel.objects.create(
                tournament=tournament,
                room=room,
                room_uuid=room.id,
                player1Local=player1,
                player2=User.objects.get(login=player2),
                start_time=timezone.now(),
                round_number=tournament.round,
                match_number=tournament.total_matches,
                player1isLocal=True)
        elif player2 in tournament.participantsLocal and player1 not in tournament.participantsLocal:
            match = TournamentMatchModel.objects.create(
                tournament=tournament,
                room=room,
                room_uuid=room.id,
                player1=User.objects.get(login=player1),
                player2Local=player2,
                start_time=timezone.now(),
                round_number=tournament.round,
                match_number=tournament.total_matches,
                player2isLocal=True)
        else:
            match = TournamentMatchModel.objects.create(
                tournament=tournament,
                room=room,
                room_uuid=room.id,
                player1=User.objects.get(login=player1),
                player2=User.objects.get(login=player2),
                start_time=timezone.now(),
                round_number=tournament.round,
                match_number=tournament.total_matches)    
  
        tournament.localMatchIP = True

        move_player_to_waitlist(tournament, player1)
        move_player_to_waitlist(tournament, player2)
        
        if player1 and player2:
            return JsonResponse({
                'name': tournament.name,
                'round': tournament.round if tournament.final == False else 'final',
                'match': tournament.total_matches,
                'player1': player1,
                'player2': player2,
                'room_id': str(room.id),
            })
    except:
        return JsonResponse({'error'})
    
def move_player_to_waitlist(tournament, player_login):
    if player_login in tournament.participantsLocal:
        tournament.participantsLocal.remove(player_login)
        tournament.waitlistLocal.append(player_login)
        tournament.save()
    else:
        try:
            user = User.objects.get(login=player_login)
            tournament.participants.remove(user)
            tournament.waitlist.add(user)
            tournament.save()
        except User.DoesNotExist:
            print(f"User with login {player_login} not found.")

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
    
def fetch_matches(tournament):
    matches = TournamentMatchModel.objects.filter(tournament=tournament)

    matches_info = []

    for match in matches:
        match_info = {
            'player1': match.player1Local if match.player1isLocal else match.player1.username,
            'player2': match.player2Local if match.player2isLocal else match.player2.username,
            'p1_score': match.p1_score,
            'p2_score': match.p2_score,
            'winner': match.winnerLocal if match.winnerLocal else match.winner.username,
            'round_number': match.round_number,
            'match_number': match.match_number,
        }
        matches_info.append(match_info)

    return matches_info

def tournament_local_end(tournament):
    matches = fetch_matches(tournament)

    return JsonResponse({
        'name': tournament.name,
        'round': 'Terminated',
        'match': tournament.total_matches,
        'tourwinner' : tournament.participantsLocal[0] if len(tournament.participantsLocal) == 1 else tournament.participants.first().login,
        'results': matches
    })

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
