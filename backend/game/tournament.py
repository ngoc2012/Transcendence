from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import RoomsModel, TournamentMatchModel, TournamentModel
from django.views.decorators.http import require_POST
from game.views import get_data
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
import uuid, json, random, requests
from accounts.models import PlayersModel
from django.db import IntegrityError
from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone
from pong.data import pong_data
from urllib.parse import quote
import random
from game.views import add_player_to_room

User = get_user_model()

# PRIMARY METHODS

def tournament_local_join_setup(request):
    game_id = request.POST.get('game_id')
    player2 = request.POST.get('player2')
    if not game_id:
        return HttpResponse("Error: No game id")
    if not player2:
        return HttpResponse("Error: No player id")

    players_key = f"{game_id}_all"
    players = cache.get(players_key) or []

    try:
        TournamentMatchModel.objects.get(room_uuid=game_id)
    except TournamentMatchModel.DoesNotExist:
        return HttpResponse("Error: Room with id " + game_id + " does not exist")

    try:
        player = PlayersModel.objects.get(login=player2)
    except PlayersModel.DoesNotExist:
        player = PlayersModel.objects.get(login='localTournament2')

    if player.id in players:
        return HttpResponse(f"Error: Player with login {player.login} is already in the room")

    room, player = add_player_to_room(game_id, player.login)
    if not room:
        return HttpResponse("Error: Room with id " + game_id + " does not exist")
    if not player:
        return HttpResponse(f"Error: Player with login {player2} does not exist")

    return JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
    })

@require_POST
def tournament_local_join(request):

    game_id = request.POST.get('game_id')
    if not game_id:
        return HttpResponse("Error: No game id!")

    try:
        room = RoomsModel.objects.get(id=game_id)
    except RoomsModel.DoesNotExist:
        return HttpResponse(f"Error: Room does not exist")

    match = TournamentMatchModel.objects.filter(room=room).first()
    if not match:
        return HttpResponse(f"Error: No match found in room with id {game_id}")

    if match.player1isLocal:
        player1 = User.objects.get(login='localTournament1')
    else:
        player1 = match.player1

    room, player = add_player_to_room(room.id, player1.login)
    if not room or not player:
        return HttpResponse("Error: Failed to add player to room.")

    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
    }))

@require_POST
def tournament_local_result(request):
    try:
        room_id = request.POST.get("room")
        score1 = request.POST.get("score1")
        score2 = request.POST.get("score2")

        match = TournamentMatchModel.objects.get(room_uuid=room_id)
        tournament = match.tournament

        update_match(match, score1, score2)
        update_tournament(tournament, match, score1, score2)
        check_new_round(tournament)
        return JsonResponse({'status': 'ok'})

    except ValueError:
        return JsonResponse({'error': 'Invalid input for scores. Please provide numeric values.'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Room or match not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred: {}'.format(str(e))}, status=500)

@require_POST
def tournament_local_get(request):
    tour_id = request.POST.get("id")
    if not tour_id:
        return JsonResponse({'error': 'No tournament ID provided'}, status=400)

    try:
        tournament = TournamentModel.objects.get(id=tour_id)

        if tournament.rematchIP:
            return tournament_matchIP(tournament)

        if tournament.ready == False:
            return JsonResponse({'error': 'not ready'})

        all_participants, all_waitlist = get_tournament_data(tournament)

        if len(all_participants) == 1 and not all_waitlist:
            tournament.terminated = True
            tournament.save()
            return tournament_local_end(tournament)

        all_participants = update_status(tournament, all_participants, all_waitlist)
        all_participants, player1, player2 = prepare_round(tournament, all_participants)
        room = gen_room(tournament)
        match = gen_match(tournament, room, player1, player2)

        move_player_to_waitlist(tournament, player1)
        move_player_to_waitlist(tournament, player2)

        player1Name, player2Name = check_alias(match, player1, player2)

        if player1 and player2:
            return JsonResponse({
                'name': tournament.name,
                'round': tournament.round if tournament.final == False else 'final',
                'match': tournament.total_matches,
                'player1' : player1Name,
                'player2': player2Name,
                'room_id': str(room.id),
            })

    except TournamentModel.DoesNotExist as e:
        return JsonResponse({'error': 'Tournament not found'}, status=404)
    except ValueError as e:
        if tournament:
            url = f"http://blockchain:9000/delete_tournament/{tournament.name}"
            tournament.delete()
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        if tournament:
            url = f"http://blockchain:9000/delete_tournament/{tournament.name}"
            tournament.delete()
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@require_POST
def tournament_add_user(request):
    try:
        data = json.loads(request.body)

        login = data.get('login')
        password = data.get('password')
        userLogin = data.get('userLogin', 'false')
        tournament_id = data.get('id')

        try:
            tournament = TournamentModel.objects.get(id=tournament_id)
        except TournamentModel.DoesNotExist:
            return JsonResponse({'error': 'Tournament not found'}, status=404)

        if userLogin == 'false':
            return add_local_player(tournament, login)
        else:
            return add_user_player(request, tournament, login, password)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

def tournament_2FAback(request):
    id = request.session.get('tourID', None)
    login = request.session.get('login2FA', None)
    if not id or not login:
        return JsonResponse({'error': 'Session data missing or incomplete'}, status=400)

    if login != request.POST.get('login'):
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    try:
        tournament = TournamentModel.objects.get(id=id)
        user = User.objects.get(login=login)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, status=404)

    tournament.participants.add(user)
    tournament.callback = False
    tournament.save()

    all_participants = get_tournament_participants(tournament)
    participants_data = [
    {'login': login} for login in all_participants if login != tournament.owner.login]

    return JsonResponse({'participants': participants_data, 'id': tournament.id})


def add_player_to_blockchain(tournament_name, login):
    player_data = {
        'id': 0,
        'login': login,
        'elo': 0,
    }
    url = f"http://blockchain:9000/add_player/"
    data = {"name": tournament_name, "player": player_data}
    response = requests.post(url, json=data)
    response.raise_for_status()


@require_POST
def tournament_local_verify(request):
    try:
        data = json.loads(request.body)
        id = data.get('id')

        if not id:
            return JsonResponse({'error': 'Missing id'}, status=400)


        tournament = TournamentModel.objects.get(id=id)
        tournament.ready = True
        tournament.save()

        if not tournament.owner == request.user:
            return JsonResponse({'error': 'Owner not found'}, status=404)

        name = tournament.name
        url = f"http://blockchain:9000/add_tournament/{name}"
        response = requests.post(url)
        response.raise_for_status()

        for participant in tournament.participants.all():
            add_player_to_blockchain(tournament.name, check_alias_from_login(participant.login))

        for participant in tournament.participantsLocal:
            add_player_to_blockchain(tournament.name, participant)

    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Error decoding JSON: {str(e)}'}, status=400)
    except TournamentModel.DoesNotExist:
        return JsonResponse({'error': 'Tournament not found'}, status=400)
    except requests.exceptions.RequestException as e:
        # print(f"Error calling add_tournament_route: {e}")
        return JsonResponse({'error': 'Failed to interact with blockchain'}, status=500)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Owner not found'}, status=404)
    except IntegrityError as e:
        return JsonResponse({'error': 'Tournament could not be created'}, status=409)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    return JsonResponse({'message': 'Done', 'id': tournament.id})

# SECONDARY METHODS

def check_alias_from_login(login):
    user = User.objects.get(login=login)
    if user.tourn_alias:
        return user.tourn_alias
    else:
        return user

def get_player_name(player, is_local, local_name, tourn_alias):
        if is_local:
            return local_name
        return tourn_alias if tourn_alias else player.username

def get_player(player, is_local):
        return player if is_local else User.objects.get(login=player)

def refresh_participants(tournament):
    tournament.participants.add(*list(tournament.waitlist.all()))
    tournament.waitlist.clear()

    if tournament.waitlistLocal:
        tournament.participantsLocal.extend(tournament.waitlistLocal)
        tournament.waitlistLocal = []

    tournament.save()

def check_alias(match, player1, player2):
    if not match.player1isLocal and match.player1.tourn_alias:
        player1Name = match.player1.tourn_alias
    else:
        player1Name = player1

    if not match.player2isLocal and match.player2.tourn_alias:
        player2Name = match.player2.tourn_alias
    else:
        player2Name = player2
    return player1Name, player2Name

def get_tournament_participants(tournament):
    participants = {user.login for user in tournament.participants.all()}
    local_participants = set(tournament.participantsLocal or [])
    all_participants = participants.union(local_participants)
    return all_participants


def get_tournament_data(tournament):
    participants = {user.login for user in tournament.participants.all()}
    waitlist = {user.login for user in tournament.waitlist.all()}

    all_participants = participants.union(tournament.participantsLocal or [])
    all_waitlist = waitlist.union(tournament.waitlistLocal or [])

    return list(all_participants), list(all_waitlist)

def update_status(tournament, all_participants, all_waitlist):
    if len(all_participants) == 2 and not all_waitlist:
        tournament.final = True

    if tournament.newRound:
        if len(all_participants) % 2 != 0:
            random_participant = random.choice(all_participants)
            all_participants.remove(random_participant)
            move_player_to_waitlist(tournament, random_participant)
        tournament.newRound = False

    tournament.save()
    return all_participants

def gen_room(tournament):
    room = RoomsModel.objects.create(
            game=tournament.game,
            name=f"{tournament.name} - Match {tournament.total_matches}",
            owner=tournament.owner,
            tournamentRoom=True
    )
    if room.game == 'pong':
        cache.set(str(room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(str(room.id) + "_y", pong_data['HEIGHT'] / 2)
    return room

def prepare_round(tournament, all_participants):
    tournament.total_matches += 1
    tournament.save()
    random.shuffle(all_participants)
    player1 = all_participants[0]
    player2 = all_participants[1]
    return all_participants, player1, player2

def tournament_matchIP(tournament):
    try:
        last_match = TournamentMatchModel.objects.filter(tournament=tournament).order_by('-match_number').first()
        if not last_match:
            return JsonResponse({'error': 'No matches found for this tournament.'}, status=404)
    except TournamentMatchModel.DoesNotExist:
        return JsonResponse({'error': 'Invalid tournament.'}, status=404)


    tournament.rematchIP = False
    tournament.save()

    if last_match.player1isLocal:
        player1 = last_match.player1Local
    else:
        player1 = last_match.player1.login

    if last_match.player2isLocal:
        player2 = last_match.player2Local
    else:
        player2 = last_match.player2.login

    player1Name, player2Name = check_alias(last_match, player1, player2)

    response_data = {
        'name': tournament.name,
        'round': 'final' if tournament.final else tournament.round,
        'match': tournament.total_matches,
        'player1': player1Name,
        'player2': player2Name,
        'room_id': str(last_match.room_uuid),
    }
    return JsonResponse(response_data)

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
            pass
            # print(f"User with login {player_login} not found.")

def fetch_matches(tournament):
    matches = TournamentMatchModel.objects.filter(tournament=tournament)

    matches_info = []

    for match in matches:
        match_info = {
            'player1': match.player1Local if match.player1isLocal else (match.player1.username if not match.player1.tourn_alias else match.player1.tourn_alias),
            'player2': match.player2Local if match.player2isLocal else (match.player2.username if not match.player2.tourn_alias else match.player2.tourn_alias),
            'p1_score': match.p1_score,
            'p2_score': match.p2_score,
            'winner': match.winnerLocal if match.winnerLocal else (match.winner.username if not match.winner.tourn_alias else match.winner.tourn_alias),
            'round_number': match.round_number,
            'match_number': match.match_number,
        }
        matches_info.append(match_info)

    return matches_info

def tournament_local_end(tournament):
    matches = fetch_matches(tournament)

    winner = tournament.participantsLocal[0] if len(tournament.participantsLocal) == 1 else (tournament.participants.first().login if not tournament.participants.first().tourn_alias else tournament.participants.first().tourn_alias)

    url = f"http://blockchain:9000/add_winner/"
    data = {"name": tournament.name, "winner": winner}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return JsonResponse({
        'name': tournament.name,
        'round': 'Terminated',
        'match': tournament.total_matches,
        'tourwinner': tournament.participantsLocal[0] if len(tournament.participantsLocal) == 1 else (tournament.participants.first().login if not tournament.participants.first().tourn_alias else tournament.participants.first().tourn_alias),
        'results': matches
    })

def gen_match(tournament, room, player1, player2):
    player1_is_local = player1 in tournament.participantsLocal
    player2_is_local = player2 in tournament.participantsLocal

    if player1_is_local and player2_is_local:
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

    elif player1_is_local and not player2_is_local:
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
    elif player2_is_local and not player1_is_local:
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

    # tournament.localMatchIP = True
    tournament.save()
    return match

# ADD USERS

def add_local_player(tournament, login):
    try:
        user = User.objects.get(login=login)
        if login in tournament.participantsLocal:
            return JsonResponse({'error': f'Player {login} already added to the tournament'}, status=400)
        return JsonResponse({'error': f'Player {login} already exists'}, status=400)

    except User.DoesNotExist:
        if login not in tournament.participantsLocal:
            tournament.participantsLocal.append(login)
            tournament.save()

    return JsonResponse({'success': True, 'login': login, 'local': True})

def add_user_player(request, tournament, login, password):
    try:
        user = User.objects.get(login=login)
        if not user.check_password(password):
            return JsonResponse({'error': f'Player {login} password is incorrect'}, status=400)

        if user in tournament.participants.all():
            return JsonResponse({'error': f'Player {login} already added to the tournament'}, status=400)

        if user.secret_2fa:
            request.session['tourID'] = str(tournament.id)
            request.session['login2FA'] = user.login
            tournament.callback = True
            tournament.save()
            return JsonResponse({'success': 'twofa', 'login': login, 'name': user.name, 'email': user.email})

        else:
            tournament.participants.add(user)
            tournament.save()

        return JsonResponse({'success': True, 'login': login, 'local': False})

    except User.DoesNotExist:
        return JsonResponse({'error': f'Player {login} not found'}, status=400)

# RESULTS

def update_match(match, score1, score2):
    match.end_time = timezone.now()
    match.p1_score = score1
    match.p2_score = score2

    if score1 > score2:
        if match.player1isLocal:
            match.winnerLocal = match.player1Local
            winblock = match.player1Local
        else:
            match.winner = match.player1
            if match.player1.tourn_alias:
                winblock = match.player1.tourn_alias
            else:
                winblock = match.player1.login
    else:
        if match.player2isLocal:
            match.winnerLocal = match.player2Local
            winblock = match.player2Local
        else:
            match.winner = match.player2
            if match.player2.tourn_alias:
                winblock = match.player2.tourn_alias
            else:
                winblock = match.player2.login

    match.save()
    if match.player1isLocal:
        blockplayer1 = match.player1Local
    else:
        if match.player1.tourn_alias:
            blockplayer1 = match.player1.tourn_alias
        else:
            blockplayer1 = match.player1.login

    if match.player2isLocal:
        blockplayer2 = match.player2Local
    else:
        if match.player2.tourn_alias:
            blockplayer2 = match.player2.tourn_alias
        else:
            blockplayer2 = match.player2.login

    player1_data = {
        'id': 0,
        'login': blockplayer1,
        'elo': 0,
        'score': match.p1_score
    }
    player2_data = {
        'id': 0,
        'login': blockplayer2,
        'elo': 0,
        'score': match.p2_score
    }
    match_data = {
        'name': match.tournament.name,
        'winner': winblock,
        'round': match.match_number,
    }
    url = f"http://blockchain:9000/add_match/"
    data = {"match": match_data, "player1": player1_data, "player2": player2_data}
    response = requests.post(url, json=data)
    response.raise_for_status()


def update_tournament(tournament, match, score1, score2):
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

    # tournament.localMatchIP = False
    tournament.save()

def check_new_round(tournament):
    db_participants = tournament.participants.all().values_list('login', flat=True)
    local_participants = getattr(tournament, 'participantsLocal', [])
    all_participants = list(db_participants) + local_participants
    if len(all_participants) == 0:
        tournament.round += 1
        tournament.newRound = True
        refresh_participants(tournament)
    tournament.save()
