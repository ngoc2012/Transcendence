from asgiref.sync import sync_to_async

from game.models import PlayersModel, PlayerRoomModel
from pong.data import pong_data
from .game import change_server

from django.contrib.auth.hashers import make_password
import pyotp

import requests

from django.core.cache import cache
from backend.game.views import add_player_to_room

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
    add_player_to_room(consumer.room_id, 'ai')

    print("AI player created. Send request to AI server.")
    with requests.post("http://ai:5000/ai/new",
        data = {
            'room_id': consumer.room.id,
            'player_id': player.id
        }) as response:
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
        print(response.text)
