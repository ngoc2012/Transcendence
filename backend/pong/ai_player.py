from asgiref.sync import sync_to_async

from accounts.models import PlayersModel
from pong.data import pong_data
from .game import change_server

from django.contrib.auth.hashers import make_password
import pyotp

from django.contrib.auth import get_user_model

import requests

from django.core.cache import cache
from game.views import add_player_to_room
from .game import remove_player

@sync_to_async
def ai_player(consumer):
    try:
        player = PlayersModel.objects.get(login='ai')
    except PlayersModel.DoesNotExist:
        print("Error: AI player not found.")
    if cache.get(consumer.k_ai) == True:
        cache.set(consumer.k_ai, False)
        print("AI player deleted.")
        with requests.post("http://ai:5000/ai/del",
            data = {
                'room_id': consumer.room_id,
                'player_id': player.id
            },
            headers={'X-Internal-Request': 'true'}) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
        remove_player(consumer, player.id)
        print("Delete ai_player", player.id, cache.get(consumer.k_server), type(player.id), player.id == cache.get(consumer.k_server))
        if player.id == cache.get(consumer.k_server):
            change_server(consumer)
        return
    else:
        cache.set(consumer.k_ai, True)
    try:
        player = PlayersModel.objects.get(login='ai')
    except PlayersModel.DoesNotExist:
        hashed_password = make_password('password_ai')
        mysecret = pyotp.random_base32()
        # player = PlayersModel(
        #     login='ai',
        #     password=hashed_password,
        #     name='AI player',
        #     email='',
        #     secret_2fa = mysecret
        # )
        # player.save()
        User = get_user_model()
        player = User.objects.create_user(
            username='ai',
            email='',
            password=hashed_password,
            name='AI player',
            secret_2fa = mysecret
        )
    add_player_to_room(consumer.room_id, 'ai')

    print("AI player created. Send request to AI server.")
    with requests.post("http://ai:5000/ai/new",
        data = {
            'room_id': consumer.room.id,
            'player_id': player.id
        },
        headers={'X-Internal-Request': 'true'}) as response:
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
