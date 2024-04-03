from asgiref.sync import sync_to_async

from game.models import PlayersModel, RoomsModel, PlayerRoomModel
from pong.data import pong_data

from django.contrib.auth.hashers import make_password

import pyotp
import time

def hit_position(x, p0, p1):
    if p0[0] == p1[0]:
        return -1
    y = (x - p0[0]) / (p1[0] - p0[0]) * (p1[1] - p0[1]) + p0[1]
    while y < 0 or y > pong_data['HEIGHT']:
        if y < 0:
            y = -y
        if y > pong_data['HEIGHT']:
            y = 2 * pong_data['HEIGHT'] - y
    return y

def ai_listener(consumer, ai_player):
    room_id = consumer.room_id
    print("AI player started.")
    # print(consumer.room.ai_player)
    last_pos = (consumer.room.x, consumer.room.y)
    curr_pos = (consumer.room.x, consumer.room.y)
    check_time = time.time()
    room = RoomsModel.objects.get(id=room_id)
    while room.ai_player:
        if (check_time + 1 < time.time()):
            check_time = time.time()
            try:
                consumer.room = RoomsModel.objects.get(id=room_id)
            except RoomsModel.DoesNotExist:
                print("Room with ID {consumer.room_id} does not exist.")
                break
            curr_pos = (consumer.room.x, consumer.room.y)
            # if consumer.room.ai_player:
            #     if consumer.room.y + pong_data['PADDLE_HEIGHT'] / 2 > ai_player.y + pong_data['PADDLE_HEIGHT'] / 2:
            #         ai_player.y += pong_data['STEP']
            #     elif consumer.room.y + pong_data['PADDLE_HEIGHT'] / 2 < ai_player.y + pong_data['PADDLE_HEIGHT'] / 2:
            #         ai_player.y -= pong_data['STEP']
            #     ai_player.save()
            if last_pos[0] != curr_pos[0]:
                y = hit_position(ai_player.x, last_pos, curr_pos)
                if ai_player.y < y:
                    ai_player.y += pong_data['STEP']
                else:
                    ai_player.y -= pong_data['STEP']
                ai_player.save()
                last_pos = curr_pos
        time.sleep(0.02)
        try:
            room = RoomsModel.objects.get(id=room_id)
        except RoomsModel.DoesNotExist:
            print("Room with ID {consumer.room_id} does not exist.")
            break
    print("AI player stopped.")

from multiprocessing import Process
@sync_to_async
def ai_player(consumer):
    if consumer.room.ai_player:
        consumer.room.ai_player = False
        consumer.room.save()
        try:
            player = PlayersModel.objects.get(login='ai')
        except PlayersModel.DoesNotExist:
            print("Error: AI player not found.")
        PlayerRoomModel.objects.get(room=consumer.room.id, player=player.id).delete()
        return
    else:
        consumer.room.ai_player = True
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
    ai_player.x = position * pong_data['PADDLE_WIDTH'] + position * pong_data['PADDLE_DISTANCE']
    if side == 1:
        ai_player.x = pong_data['WIDTH'] - ai_player.x - pong_data['PADDLE_WIDTH']
    ai_player.y = pong_data['HEIGHT'] / 2 - pong_data['PADDLE_HEIGHT'] / 2
    ai_player.save()
    ai_process = Process(target=ai_listener, args=(consumer, ai_player))
    ai_process.start()