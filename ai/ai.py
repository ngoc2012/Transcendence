from flask import Flask
from flask import request

# Create an instance of the Flask class
app = Flask(__name__)

ai_processus = {}

import sys
from multiprocessing import Process
import time

from .data import pong_data

table_height = pong_data['HEIGHT'] - pong_data['RADIUS'] * 2

import math
def mirror(n_floors, y):
    if n_floors >= 0:
        return math.ceil(n_floors / 2) * 2 * table_height + pow(-1, n_floors) * y
    return -math.floor(-n_floors / 2) * 2 * table_height + pow(-1, -n_floors) * y

def unmirror(y):
    n_rebound = math.floor(y / table_height)
    return (y - math.ceil(n_rebound / 2) * 2 * table_height) / pow(-1, abs(n_rebound))

def rebound(pos):
    max_rebound = 2
    for sign in [1, -1]:
        for i in range(max_rebound):
            for j in range(max_rebound):
                x = [k[0] for k in pos]
                y = [pos[0][1], mirror(sign * i, pos[1][1]), mirror(sign * (i + j), pos[2][1])]
                # print(pos, i * sign, sign * (i + j))
                # print(x, y)
                if y[2] == y[1]:
                    return 0
                if x[2] - x[0] == 0:
                    return -100
                n = (x[2] - x[1]) * (y[2] - y[0]) / ( (x[2] - x[0]) * (y[2] - y[1]) )
                # print((x[2] - x[1]) * (y[2] - y[0]), (x[2] - x[0]) * (y[2] - y[1]), n)
                if n >= 0.98 and n <= 1.02:
                # if n == 1.0:
                    return sign * i
    return -100

def hit_position(x, p0, p1):
    if p0[0] == p1[0]:
        return -1
    y = (x - p0[0]) / (p1[0] - p0[0]) * (p1[1] - p0[1]) + p0[1]
    # print("hit y: " + str(y) + " x: " + str(x) + " p0: " + str(p0) + " p1: " + str(p1), unmirror(y))
    return unmirror(y)

import requests

def ai_listener(room_id, player_id):
    print(f"AI process started for room {room_id} and player {player_id}.")
    pos = []
    # hits = []
    delay = 0.03
    max_steps = 10
    while True:
        n = 0
        with requests.get("http://django:8000/pong/" + room_id + '/' + player_id + '/state', verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                break
            if response.text == "NULL":
                print("Room does not exist.")
                break
            state = response.json()
            if int(player_id) not in state['team0'] and int(player_id) not in state['team1']:
                print("No AI player found.")
                break
            if not state['started']:
                if len(pos) > 1:
                    del pos[:]
                elif len(pos) == 1:
                    pos[0] = (state['ball']['x'], state['ball']['y'])
                else:
                    pos.append((state['ball']['x'], state['ball']['y']))
            if (int(player_id) in state['team0'] and state['dx'] == -1) or (int(player_id) in state['team1'] and state['dx'] == 1):
                if state['started']:
                    pos.append((state['ball']['x'], state['ball']['y'] - pong_data['RADIUS']))
                if len(pos) > 2:
                    rebound_value = rebound(pos[-3:])
                    # print("Rebound value: " + str(rebound_value))
                    if rebound_value != -100:
                        hit = hit_position(state['x'], pos[-3], (pos[-2][0], mirror(rebound_value, pos[-2][1]))) + pong_data['RADIUS']
                        # print(hit, state)
                        while n < max_steps and (hit <= state['y'] or hit >= state['y'] + pong_data['PADDLE_HEIGHT']):
                            if state['y'] + pong_data['PADDLE_HEIGHT'] / 2 < hit:
                                com = 'down'
                            else:
                                com = 'up'
                            with requests.get("http://django:8000/pong/" + room_id + '/' + player_id + '/' + com,verify=False) as response:
                                if response.status_code != 200:
                                    print("Request failed with status code:", response.status_code)
                                    break
                                if response.text == "NULL":
                                    print("Room does not exist.")
                                    break
                                state = response.json()
                            # print(com, state['y'])
                            time.sleep(delay)
                            n += 1
            else:
                del pos[:]
                if n < max_steps and abs((state['y'] + pong_data['PADDLE_HEIGHT']) / 2 - pong_data['HEIGHT'] / 2) > pong_data['PADDLE_HEIGHT']:
                    if state['y'] + pong_data['PADDLE_HEIGHT'] / 2 < pong_data['HEIGHT'] / 2:
                        com = 'down'
                    else:
                        com = 'up'
                    with requests.get("http://django:8000/pong/" + room_id + '/' +player_id + '/' + com,verify=False) as response:
                        if response.status_code != 200:
                            print("Request failed with status code:", response.status_code)
                            break
                        if response.text == "NULL":
                            print("Room does not exist.")
                            break
                        state = response.json()
                    # print(com, state['y'])
                    time.sleep(delay)
                    n += 1
        if not state['ai_player']:
            print("AI player is not active.")
            break
        if room_id not in ai_processus:
            print("AI process does not exist.")
            break
        time.sleep(1.0 - n * delay)
    print(f"AI process ended for room {room_id} and player {player_id}.")

@app.route('/ai/new', methods=['POST', 'GET'])
def new():
    room_id = request.form.get('room_id')
    player_id = request.form.get('player_id')
    sys.stderr.write("Start AI process\n")
    ai_process = Process(target=ai_listener, args=(room_id, player_id))
    ai_processus[room_id] = {ai_process}
    ai_process.start()
    return "new/" + str(room_id) + "/" + str(player_id)

@app.route('/ai/del', methods=['POST', 'GET'])
def delete():
    room_id = request.form.get('room_id')
    player_id = request.form.get('player_id')
    # ai_processus[room_id].join()
    del ai_processus[room_id]
    print("AI process ended.")
    return "Deleted " + str(room_id) + "/" + str(player_id)

if __name__ == "__main__":
    app.run(debug=True)
