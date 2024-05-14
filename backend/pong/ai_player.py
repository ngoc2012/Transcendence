from asgiref.sync import sync_to_async

from accounts.models import PlayersModel
from pong.data import pong_data
from pong.game import change_server

from django.contrib.auth.hashers import make_password
import pyotp

from django.contrib.auth import get_user_model

import requests

from django.core.cache import cache
from pong.game import remove_player

@sync_to_async
def ai_player(consumer):
    from game.views import add_player_to_room
    try:
        player = PlayersModel.objects.get(login='ai')
    except PlayersModel.DoesNotExist:
        pass
    if cache.get(consumer.k_ai) == True:
        cache.set(consumer.k_ai, False)
        with requests.post("http://ai:5000/ai/del",
            data = {
                'room_id': consumer.room_id,
                'player_id': player.id
            },
            headers={'X-Internal-Request': 'true'}) as response:
            if response.status_code != 200:
                pass
        remove_player(consumer, player.id)
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
        User = get_user_model()
        player = User.objects.create_user(
            username='ai',
            email='',
            password=hashed_password,
            name='AI player',
            secret_2fa = mysecret
        )
    add_player_to_room(consumer.room_id, 'ai')

    with requests.post("http://ai:5000/ai/new",
        data = {
            'room_id': consumer.room.id,
            'player_id': player.id
        },
        headers={'X-Internal-Request': 'true'}) as response:
        if response.status_code != 200:
            pass
