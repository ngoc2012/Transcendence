import requests
import json
import asyncio
import ssl
import websockets
from websockets import exceptions as ws_exceptions

# Disable SSL-related warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

host = "127.0.0.1:8080"
certfile = "minh-ngu.crt"
keyfile = "minh-ngu.key"

import multiprocessing
main_queue = multiprocessing.Queue()

async def rooms_listener():
    global main_queue
    uri = "wss://" + host + "/ws/game/rooms/"
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as rooms_socket:
            while True:
                response = await rooms_socket.recv()
                rooms = json.loads(response)
                if isinstance(rooms, list):
                    main_queue.put(('rooms', rooms))
                
                # await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Rooms websocket connection closed.")
    print("Rooms listener end")

async def pong_listener(room):
    global main_queue
    
    uri = "wss://" + host + "/ws/pong/" + room['id'] + '/' + room['player_id'] + '/'
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as pong_socket:
            while True:
                response = await pong_socket.recv()
                main_queue.put(('pong', json.loads(response)))
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Pong websocket connection closed.")

def join(game_id, login):
    try:
        print("Joining game:", game_id)
        response = requests.post("https://" + host + "/game/join",
            data={"login": login, "game_id": game_id}, 
            cert=(certfile, keyfile),
            verify=False)
        # print(response)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            return None
        if "error" in response.text.lower():
            print(response.text)
            return None
        return json.loads(response.text)
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return None
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return None
    return None
    
import keyboard
def keyboard_listener():
    # print('Keyboard listener')
    global main_queue
    while True:
        key_event = keyboard.read_event(suppress=True)
        if key_event.event_type == keyboard.KEY_DOWN:
            key = key_event.name
            # print('Key:', key)
            main_queue.put(('key', key))
            if key == 'esc':
                break

def log_in():
    global login
    # login = input("Login: ")
    # password = getpass.getpass("Password: ")
    login = "admin"
    password = "admin"
    try:
        response = requests.post("https://" + host + "/log_in/",
            data={"login": login, "password": password}, 
            cert=(certfile, keyfile),
            verify=False)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            exit(1)
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        exit(1)
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        exit(1)

import signal
def signal_handler(signal, frame):
    exit(0)

def run_rooms_listener():
    asyncio.run(rooms_listener())

def run_pong_listener(room):
    asyncio.run(pong_listener(room))

import curses

def draw_pong(room, state):
    HEIGHT = int(room['data']['HEIGHT'] / 5)
    WIDTH = int(room['data']['WIDTH'] / 5)
    PADDLE_WIDTH = int(room['data']['PADDLE_WIDTH'] / 5)
    PADDLE_HEIGHT = int(room['data']['PADDLE_HEIGHT'] / 5)

    s = curses.initscr()
    curses.curs_set(0)
    # sh, sw = s.getmaxyx()
    w = curses.newwin(HEIGHT + 3, WIDTH + 2, 0, 0)
    # w.keypad(1)
    # w.timeout(100)

    w.clear()
    # w.refresh()

    paddle = '█' * PADDLE_WIDTH
    ball = ['◜', '◝', '◟', '◞']
    border = '█'

    # Draw horizontal border
    for j in range(WIDTH + 2):
        w.addch(0, j, border)  # Top border
        w.addch(HEIGHT + 1, j, border)  # Bottom border

    # Draw vertical border
    for i in range(HEIGHT + 1):
        w.addch(i, 0, border)  # Left border
        w.addch(i, WIDTH + 1, border)  # Right border

    # Draw paddles
    for p in state['players']:
        for i in range(PADDLE_HEIGHT):
            if int(p['y'] / 5) + i >= 0:
                w.addstr(int(p['y'] / 5) + i, int(p['x'] / 5 + 1), paddle)

    # Draw ball
    for i in range(2):
        for j in range(2):
            w.addch(int(state['ball']['y'] / 5) + i - 1, int(state['ball']['x'] / 5) + j - 1, ball[i * 2 + j])
    w.refresh()

from multiprocessing import Process
if __name__ == "__main__":
    log_in()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    rooms_process = Process(target=run_rooms_listener)
    rooms_process.start()

    keys_process = Process(target=keyboard_listener)
    keys_process.start()

    pong_process = None
    rooms = []
    room = None

#     room: {'id': '8242ffeb-386b-4080-bfba-00b265295405', 'game': 'pong', 'name': 'Stars war', 'player_id': '8d8d3127-7a3a-4463-a29c-62e95959a0e8', 'data': {'HEIGHT': 400, 'WIDTH': 800, 'RADIUS': 10, 'STEP': 20, 'STEP_X': 20, 'DX': 5, 'DY': 5, 'PADDLE_WIDTH': 10, 'PADDLE_HEIGHT': 60, 'PADDLE_STEP': 5, 'PADDLE_DISTANCE': 20}}
# Connecting to wss://127.0.0.1:8080/ws/pong/8242ffeb-386b-4080-bfba-00b265295405/8d8d3127-7a3a-4463-a29c-62e95959a0e8/...
# Pong: {'team0': ['sdafsdaf'], 'team1': ['dfgdsfg']}
# Pong: {'score': [0, 0]}
# Pong: {'ball': {'x': 20, 'y': 200}, 'players': [{'x': 0, 'y': 170}, {'x': 790, 'y': 170}]}
# Pong: {'ball': {'x': 20, 'y': 180}, 'players': [{'x': 790, 'y': 170}, {'x': 0, 'y': 150}]}
# Pong: {'ball': {'x': 40, 'y': 180}, 'players': [{'x': 790, 'y': 170}, {'x': 20, 'y': 150}]}
    while True:
        p, data = main_queue.get()
        # print('p:', p, ',data:', data, flush=True)
        if p == 'rooms':
            rooms = data
            print('\033c')
            print("[0..9]: join game | n: new game | Esc: quit", flush=True)
            for i, r in enumerate(rooms):
                print(str(i) + ' - ' + r['name'] + ' - ' + r['id'])
            
        elif p == 'key':
            # print('Pong:', data)
            if data == 'esc':
                break
            elif data.isdigit():
                if (int(data) < 0) or (int(data) >= len(rooms)):
                    print('Invalid game number')
                    continue
                room = join(rooms[int(data)]['id'], login)
                if room != None:
                    if rooms_process != None:
                        rooms_process.terminate()
                        rooms_process.join()
                        rooms_process = None
                    pong_process = Process(target=run_pong_listener, args=(room,))
                    pong_process.start()
            elif data == 'q':
                if pong_process != None:
                    pong_process.terminate()
                    pong_process.join()
                if rooms_process == None:
                    rooms_process = Process(target=run_rooms_listener)
                    rooms_process.start()
            elif data in ['up', 'down', 'left', 'right']:
                if room != None:
                    response = requests.get("https://" + host + "/pong/" + room['id'] + '/' + room['player_id'] + '/' + data,
                    cert=(certfile, keyfile),
                    verify=False)
        elif p == 'pong':
            if 'ball' in data.keys():
                draw_pong(room, data)
    # curses.endwin()
    if rooms_process != None:
        rooms_process.terminate()
        rooms_process.join()
    if pong_process != None:
        pong_process.terminate()
        pong_process.join()
    keys_process.join()
