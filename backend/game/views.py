from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RoomsModel, PlayersModel, PlayerRoomModel, TournamentModel, TournamentMatchModel

import jwt
from pong.data import pong_data
import os
from datetime import datetime, timedelta

from django.core.cache import cache

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

def get_data(game):
    if game == 'pong':
        return pong_data
    return {}

@csrf_exempt
def new_game(request):
    if 'game' not in request.POST:
        return (HttpResponse("Error: No game!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'name' not in request.POST:
        return (HttpResponse("Error: No name!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    owner = PlayersModel.objects.get(login=request.POST['login'])
    new_room = RoomsModel(
        game=request.POST['game'],
        name=request.POST['name'],
        owner=owner,
        server=owner
    )
    if new_room.game == 'pong':
        cache.set(str(new_room.id) + "_x", pong_data['PADDLE_WIDTH'] + pong_data['RADIUS'])
        cache.set(str(new_room.id) + "_y", pong_data['HEIGHT'] / 2)
    new_room.save()
    if new_room.game == 'pong':
        cache.set(str(new_room.id) + "_" + str(owner.id) + "_x", 0)
        cache.set(str(new_room.id) + "_" + str(owner.id) + "_y", pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2)
    return (JsonResponse({
        'id': str(new_room),
        'game': new_room.game,
        'name': new_room.name,
        'player_id': str(owner.id),
        'data': get_data(new_room.game)
        }))

@csrf_exempt
def update(request):
    data = [
        {
            "id": str(i),
            "name": i.name
        } for i in RoomsModel.objects.all()
    ]
    # print(data)
    return JsonResponse(data, safe=False)

def add_player_to_room(game_id, login):
    if not RoomsModel.objects.filter(id=game_id).exists():
        return None, None
    room = RoomsModel.objects.get(id=game_id)

    if not PlayersModel.objects.filter(login=login).exists():
        return room, None
    player = PlayersModel.objects.get(login=login)

    k_team0 = str(room.id) + "_team0"
    k_team1 = str(room.id) + "_team1"
    team0 = cache.get(k_team0)
    team1 = cache.get(k_team1)
    n0 = len(team0)
    n1 = len(team1)
    if n1 > n0:
        cache.set(k_team0, team0.append(player.id))
        position = n0
    else:
        cache.set(k_team1, team1.append(player.id))
        position = n1
    team1 = cache.get(k_team1)
    if room.game == 'pong':
        k_player_x = str(room.id) + "_" + str(player.id) + "_x"
        k_player_y = str(room.id) + "_" + str(player.id) + "_y"
        cache.set(k_player_x, position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE'])
        if player.id in team1:
            cache.set(k_player_x, pong_data['WIDTH'] - cache.get(k_player_x) - pong_data['PADDLE_WIDTH'])
        cache.set(k_player_y, pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2)
    return room, player

@csrf_exempt
def join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    
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

#delete a room with a JWT check
@csrf_exempt
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

    if PlayerRoomModel.objects.filter(room=room.id).count() > 0:
        return JsonResponse({'error': "Someone is still playing"}, status=401)
    
    #JWT token check
    if 'Authorization' not in request.headers:
        return JsonResponse({'error': 'Authorization header missing'}, status=401)
    auth_header = request.headers['Authorization']
    try:
        token_type, token = auth_header.split(' ')
        if token_type != 'Bearer':
            return JsonResponse({'error': 'Invalid token type'}, status=401)
    except ValueError:
        return JsonResponse({'error': 'Malformed Authorization header'}, status=401)

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        player_id = payload['user_id']
        if player_id != player.id:
            return JsonResponse({'error': 'Invalid JWT token'}, status=401)

        print("Valid JWT token used")
        room.delete()
        return JsonResponse({'message': s})

    #Token refresh handling
    except jwt.ExpiredSignatureError:
        if 'refresh_token' not in request.COOKIES:
            return JsonResponse({'error': 'JWT token expired and Refresh token missing'}, status=401)
        refresh_token = request.COOKIES.get('refresh_token')
        try:

            payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=['HS256'])

            new_token = jwt.encode({
                'user_id': player.id,
                'exp': datetime.utcnow() + timedelta(hours=1)  # Access token expiration time
            }, JWT_SECRET_KEY, algorithm='HS256')
            print("JWT token expired but a new one has been created using the Refresh token")
            room.delete()
            return JsonResponse({'message': s, 'token': new_token})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'JWT token expired and Refresh token expired, log in again'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'JWT token expired and Invalid refresh token, log in again'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def tournament_join(request):
    if 'game_id' not in request.POST:
        return (HttpResponse("Error: No game id!"))
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login " + request.POST['login'] + " does not exist!"))
    #uuid_obj = UUID(uuid_str)
    if not RoomsModel.objects.filter(id=request.POST['game_id']).exists():
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    room, player = add_player_to_room(request.POST['game_id'], request.POST['login'])
    if room == None:
        return (HttpResponse("Error: Room with id " + request.POST['game_id'] + " does not exist!"))
    if player == None:
        return (HttpResponse("Error: Player with login " + request.POST['login'] + " does not exist!"))
    match = TournamentMatchModel.objects.filter(room=room).first()
    return (JsonResponse({
        'id': str(room),
        'game': room.game,
        'name': room.name,
        'player_id': player.id,
        'data': get_data(room.game)
        }))

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
