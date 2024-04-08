from asgiref.sync import sync_to_async

from game.models import PlayersModel, PlayerRoomModel
from pong.data import pong_data
from .game import change_server

from django.contrib.auth.hashers import make_password
import pyotp

import requests

from django.core.cache import cache

@sync_to_async
def ai_player(consumer):
    if consumer.room.ai_player:
        consumer.room.ai_player = False
        cache.set(consumer.k_ai, False)
        consumer.room.save()
        try:
            player = PlayersModel.objects.get(login='ai')
        except PlayersModel.DoesNotExist:
            print("Error: AI player not found.")
        
        print("AI player deleted.")
        with requests.post("http://ai:5000/ai/del",
            data = {
                'room_id': consumer.room.id,
                'player_id': player.id
            }) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
        PlayerRoomModel.objects.get(room=consumer.room.id, player=player.id).delete()
        if consumer.room.server == player:
            change_server(consumer)
        return
    else:
        consumer.room.ai_player = True
        cache.set(consumer.k_ai, True)
        consumer.room.save()
    # print("ai player")
    try:
        player = PlayersModel.objects.get(login='ai')
    except PlayersModel.DoesNotExist:
        hashed_password = make_password('password_ai')
        mysecret = pyotp.random_base32()
        player = PlayersModel(
            login='ai',
            password=hashed_password,
            name='AI player',
            email='',
            secret_2fa = mysecret
        )
        player.save()
    
    if (PlayerRoomModel.objects.filter(room=consumer.room.id, player=player.id).count() > 0):
        print("Error: Player has been already in the game!")
        return False
    n0 = PlayerRoomModel.objects.filter(room=consumer.room, side=0).count()
    n1 = PlayerRoomModel.objects.filter(room=consumer.room, side=1).count()
    if n1 > n0:
        side = 0
        position = n0
    else:
        side = 1
        position = n1
    ai_player = PlayerRoomModel(
        player=player,
        room=consumer.room,
        side=side,
        position=position
    )
    #ai_player.x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
    #if side == 1:
    #    ai_player.x = pong_data['WIDTH'] - ai_player.x - pong_data['PADDLE_WIDTH']
    #ai_player.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
    ai_player.save()
    cache.set(str(consumer.room_id) + "_" + str(ai_player.id) + "_x", position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE'])
    if side == 1:
        cache.set(str(consumer.room_id) + "_" + str(ai_player.id) + "_x", pong_data['WIDTH'] - cache.get(str(consumer.room_id) + "_" + str(ai_player.id) + "_x") - pong_data['PADDLE_WIDTH'])
    cache.set(str(consumer.room_id) + "_" + str(ai_player.id) + "_y", pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2)
    

    print("AI player created. Send request to AI server.")
    with requests.post("http://ai:5000/ai/new",
        data = {
            'room_id': consumer.room.id,
            'player_id': player.id
        }) as response:
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
        print(response.text)
