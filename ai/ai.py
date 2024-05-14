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
                if y[2] == y[1]:
                    return 0
                if x[2] - x[0] == 0:
                    return -100
                n = (x[2] - x[1]) * (y[2] - y[0]) / ( (x[2] - x[0]) * (y[2] - y[1]) )
                if n >= 0.98 and n <= 1.02:
                    return sign * i
    return -100

def hit_position(x, p0, p1):
    if p0[0] == p1[0]:
        return -1
    y = (x - p0[0]) / (p1[0] - p0[0]) * (p1[1] - p0[1]) + p0[1]
    return unmirror(y)

import requests

def ai_listener(room_id, player_id):
    pos = []
    delay = 0.03
    max_steps = 10
    headers = {
        'X-Internal-Request': 'true'
    }
    tolerence_x = 4 * pong_data['STEP_X']
    x_min = 0
    x_max = pong_data['WIDTH'] - pong_data['PADDLE_WIDTH']
    while True:
        n = 0
        url = "http://django:8000/pong/" + room_id + '/' + player_id + '/state'
        with requests.get(url, headers=headers, verify=False) as response:
            if response.status_code != 200:
                break
            if response.text == "NULL":
                break
            state = response.json()
            if int(player_id) not in state['team0'] and int(player_id) not in state['team1']:
                break
            if not state['started']:
                if len(pos) > 1:
                    del pos[:]
                elif len(pos) == 1:
                    pos[0] = (state['ball']['x'], state['ball']['y'])
                else:
                    pos.append((state['ball']['x'], state['ball']['y']))
                if state['server']:
                    url = "http://django:8000/pong/start/" + room_id
                    with requests.get(url, headers=headers, verify=False) as response:
                        if response.status_code != 200:
                            break
            if (int(player_id) in state['team0'] and state['dx'] == -1) or (int(player_id) in state['team1'] and state['dx'] == 1):
                if state['started']:
                    pos.append((state['ball']['x'], state['ball']['y'] - pong_data['RADIUS']))
                if len(pos) > 2:
                    rebound_value = rebound(pos[-3:])
                    if rebound_value != -100:
                        x0 = round(state['x'])
                        distance = abs(state['x'] - state['ball']['x'])
                        x = x0
                        if state['power_play'] and distance > tolerence_x:
                            x0 = (state['x'] + state['ball']['x']) / 2
                        if state['power_play'] and distance > tolerence_x:
                            while n < max_steps and x >= x_min and x <= x_max and abs(x - x0) > tolerence_x:
                                if x0 < x:
                                    com = 'left'
                                    x -= pong_data['STEP_X']
                                else:
                                    com = 'right'
                                    x += pong_data['STEP_X']
                                url = "http://django:8000/pong/" + room_id + '/' + player_id + '/' + com
                                with requests.get(url, headers=headers, verify=False) as response:
                                    if response.status_code != 200:
                                        break
                                    if response.text == "NULL":
                                        break
                                    state = response.json()
                                time.sleep(delay)
                                n += 1
                        hit = hit_position(x, pos[-3], (pos[-2][0], mirror(rebound_value, pos[-2][1]))) + pong_data['RADIUS']
                        while n < max_steps and (hit <= state['y'] or hit >= state['y'] + pong_data['PADDLE_HEIGHT']):
                            if state['y'] + pong_data['PADDLE_HEIGHT'] / 2 < hit:
                                com = 'down'
                            else:
                                com = 'up'
                            url = "http://django:8000/pong/" + room_id + '/' + player_id + '/' + com
                            with requests.get(url, headers=headers, verify=False) as response:
                                if response.status_code != 200:
                                    break
                                if response.text == "NULL":
                                    break
                                state = response.json()
                            time.sleep(delay)
                            n += 1
            else:
                del pos[:]
                if int(player_id) in state['team0']:
                    dx  = state['x'] - x_min
                else:
                    dx  = state['x'] - x_max
                if n < max_steps and abs(dx) > 0:
                    if dx > 0:
                        com = 'left'
                    else:
                        com = 'right'
                    url = "http://django:8000/pong/" + room_id + '/' + player_id + '/' + com
                    for i in range(round(abs(dx) / pong_data['STEP_X'])):
                        with requests.get(url, headers=headers, verify=False) as response:
                            if response.status_code != 200:
                                break
                            if response.text == "NULL":
                                break
                            state = response.json()
                            time.sleep(delay)
                            n += 1
                dy = (state['y'] + pong_data['PADDLE_HEIGHT'] / 2) - pong_data['HEIGHT'] / 2
                if n < max_steps and abs(dy) > pong_data['PADDLE_WIDTH']:
                    if dy < 0:
                        com = 'down'
                    else:
                        com = 'up'
                    url = "http://django:8000/pong/" + room_id + '/' + player_id + '/' + com
                    for i in range(round(abs(dy) / pong_data['STEP'])):
                        with requests.get(url, headers=headers, verify=False) as response:
                            if response.status_code != 200:
                                break
                            if response.text == "NULL":
                                break
                            state = response.json()
                        time.sleep(delay)
                        n += 1
        if not state['ai_player']:
            break
        if room_id not in ai_processus:
            break
        time.sleep(1.0 - n * delay)

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
    del ai_processus[room_id]
    return "Deleted " + str(room_id) + "/" + str(player_id)

if __name__ == "__main__":
    app.run(debug=True)
