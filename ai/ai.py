from flask import Flask
from flask import request

# Create an instance of the Flask class
app = Flask(__name__)

ai_processus = {}

import sys
from multiprocessing import Process
import time

from .data import pong_data

def rebound(pos):
    max_rebound = 4
    for i in range(max_rebound):
        for j in range(max_rebound):
            x = [k[0] for k in pos]
            y = [pos[0][1], i*pos[1][1], j*pos[2][1]]
            y1 = [pos[0][1], -i*pos[1][1], -j*pos[2][1]]
            if (x[2] - x[1]) * (y[2] - y[0]) == (x[2] - x[0]) * (y[2] - y[1]):
                return i
            elif (x[2] - x[1]) * (y1[2] - y1[0]) == (x[2] - x[0]) * (y1[2] - y1[1]):
                return -i
    return None

def hit_position(x, p0, p1):
    if p0[0] == p1[0]:
        return -1
    y = (x - p0[0]) / (p1[0] - p0[0]) * (p1[1] - p0[1]) + p0[1]
    # print("hit y: " + str(y) + " x: " + str(x) + " p0: " + str(p0) + " p1: " + str(p1))
    while y < 0 or y > pong_data['HEIGHT']:
        if y < 0:
            y = -y
        if y > pong_data['HEIGHT']:
            y = 2 * pong_data['HEIGHT'] - y
    return y

import requests

def ai_listener(room_id, player_id):
    print(f"AI process started for room {room_id} and player {player_id}.")
    pos = []
    hits = []
    delay = 0.04
    max_steps = 10
    while True:
        n = 0
        with requests.get("http://django:8000/pong/" + room_id + '/' + player_id + '/state', verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                break
            else:
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
                        pos.append((state['ball']['x'], state['ball']['y']))
                    if len(pos) > 2:
                        i = len(pos) - 1
                        rebound_value = rebound(pos)
                        hits.append(hit_position(state['x'], pos[0], (pos[1][0], pos[1][1] * rebound_value)))
                        print("Rebound value: " + str(rebound_value))
                        while n < max_steps and (hits[len(hits) - 1] <= state['y'] or hits[len(hits) - 1] >= state['y'] + pong_data['PADDLE_HEIGHT']):
                            if state['y'] + pong_data['PADDLE_HEIGHT'] / 2 < hits[len(hits) - 1]:
                                com = 'down'
                            else:
                                com = 'up'
                            with requests.get("http://django:8000/pong/" + room_id + '/' + player_id + '/' + com,verify=False) as response:
                                if response.status_code != 200:
                                    print("Request failed with status code:", response.status_code)
                                    break
                            time.sleep(delay)
                            n += 1
                else:
                    del pos[:]
                    del hits[:]
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
