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
score = [0, 0]
login = ""
name = ""
team0 = []
team1 = []

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
                elif 'type' in rooms.keys():
                    if rooms['type'] == 'close' and rooms['login_id'] == login:
                        break
            # print("Rooms listener close")
            await rooms_socket.close()
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Rooms websocket connection closed.")
    # print("Rooms listener end")

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
                response_text = await pong_socket.recv()
                response = json.loads(response_text)
                if 'type' in response.keys():
                    if response['type'] == 'close' and response['player_id'] == room['player_id']:
                        break
                    elif response['type'] == 'start':
                        await pong_socket.send('start')
                main_queue.put(('pong', response))
            # print("Pong listener close")
            # await pong_socket.close()
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
        with requests.post("https://" + host + "/game/join",
            data={"login": login, "game_id": game_id}, 
            cert=(certfile, keyfile),
            verify=False) as response:
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
  
def new_game(login):
    try:
        with requests.post("https://" + host + "/game/new",
            data = {
                'name': 'Stars war',
                'game': 'pong',
                'login': login
            },
            cert=(certfile, keyfile),
            verify=False) as response:
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
    global main_queue
    while True:
        key_event = keyboard.read_event(suppress=True)
        if key_event.event_type == keyboard.KEY_DOWN:
            key = key_event.name
            # print('Key:', key)
            main_queue.put(('key', key))
            if key == 'esc':
                break

import getpass
def log_in():
    global login, name
    # login = input("Login: ")
    # password = getpass.getpass("Password: ")
    login = "admin"
    password = "admin"
    try:
        with requests.post("https://" + host + "/log_in/",
            data={"login": login, "password": password}, 
            cert=(certfile, keyfile),
            verify=False) as response:
            if response.status_code != 200:
                return False
            if "error" in response.text.lower():
                print(response.text)
                return False
            response_json = json.loads(response.text)
            if "name" in response_json.keys():
                name = response_json['name']
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return False
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return False
    return True

import getpass
def sign_up():
    global login, name
    login = input("Login: ")
    password = getpass.getpass("Password: ")
    name = input("Full Name: ")
    email = input("Email: ")
    try:
        with requests.post("https://" + host + "/new_player/",
            data={
                "login": login,
                "password": password,
                "name": name,
                "email": email,
                "enable2fa": False
            }, 
            cert=(certfile, keyfile),
            verify=False) as response:
            if response.status_code != 200:
                return False
            if "error" in response.text.lower():
                print(response.text)
                return False
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return False
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return False
    return True

# import signal
# def signal_handler(signal, frame):
#     exit(0)

def run_rooms_listener():
    asyncio.run(rooms_listener())

def run_pong_listener(room):
    asyncio.run(pong_listener(room))

import curses

def draw_pong(room, state):
    ZX = 5
    ZY = 10
    DY = 1
    HEIGHT = int(room['data']['HEIGHT'] / ZY)
    WIDTH = int(room['data']['WIDTH'] / ZX)
    PADDLE_WIDTH = int(room['data']['PADDLE_WIDTH'] / ZX)
    PADDLE_HEIGHT = int(room['data']['PADDLE_HEIGHT'] / ZY)

    s = curses.initscr()
    curses.curs_set(0)
    # sh, sw = s.getmaxyx()
    w = curses.newwin(HEIGHT + 4, WIDTH + 3, 0, 0)

    w.clear()
    # w.refresh()

    paddle = '█' * PADDLE_WIDTH
    ball = ['◜', '◝', '◟', '◞']
    border = '█'

    s = "Player: " + name + " | " + str(team0) + " vs " + str(team1) + " | " + str(score[0]) + " - " + str(score[1]) + " | Ctrl: start game | q: quit game | Esc: quit program"
    w.addstr(0, 0, s[:(WIDTH + 2)])  # Top border

    # Draw horizontal border
    for j in range(WIDTH + 1):
        w.addch(DY, j, border)              # Top border
        w.addch(HEIGHT + 1 + DY, j, border) # Bottom border

    # Draw vertical border
    for i in range(HEIGHT + 2):
        w.addch(i + DY, 0, border)          # Left border
        w.addch(i + DY, WIDTH + 1, border)  # Right border

    # Draw paddles
    for p in state['players']:
        for i in range(PADDLE_HEIGHT):
            if int(p['y'] / ZY) + i + 1 >= 0:
                w.addstr(int(p['y'] / ZY) + i + 1 + DY, int(p['x'] / ZX) + 1, paddle)

    # Draw ball
    for i in range(2):
        for j in range(2):
            w.addch(int(state['ball']['y'] / ZY) + i + DY, int(state['ball']['x'] / ZX) + j, ball[i * 2 + j])
    w.refresh()

from multiprocessing import Process
if __name__ == "__main__":
    while not log_in():
        print("Login failed")
        choice = input("0: retry login | 1: sign up | 2: quit program\nYour choice : ")
        if choice == '0':
            next
        elif choice == '1':
            while not sign_up():
                print("Sign up failed")
                choice = input("Any key: retry sign up | 2: quit program\nYour choice : ")
                if choice == '2':
                    exit(0)
            break
        elif choice == '2':
            exit(0)

    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)
    rooms_process = Process(target=run_rooms_listener)
    rooms_process.start()

    keys_process = Process(target=keyboard_listener)
    keys_process.start()

    pong_process = None
    rooms = []
    room = None
    playing = False

#     room: {'id': '8242ffeb-386b-4080-bfba-00b265295405', 'game': 'pong', 'name': 'Stars war', 'player_id': '8d8d3127-7a3a-4463-a29c-62e95959a0e8', 'data': {'HEIGHT': 400, 'WIDTH': 800, 'RADIUS': 10, 'STEP': 20, 'STEP_X': 20, 'DX': 5, 'DY': 5, 'PADDLE_WIDTH': 10, 'PADDLE_HEIGHT': 60, 'PADDLE_STEP': 5, 'PADDLE_DISTANCE': 20}}
# Connecting to wss://127.0.0.1:8080/ws/pong/8242ffeb-386b-4080-bfba-00b265295405/8d8d3127-7a3a-4463-a29c-62e95959a0e8/...
# Pong: {'team0': ['sdafsdaf'], 'team1': ['dfgdsfg']}
# Pong: {'score': [0, 0]}
# Pong: {'ball': {'x': 20, 'y': 200}, 'players': [{'x': 0, 'y': 170}, {'x': 790, 'y': 170}]}
# Pong: {'ball': {'x': 20, 'y': 180}, 'players': [{'x': 790, 'y': 170}, {'x': 0, 'y': 150}]}
# Pong: {'ball': {'x': 40, 'y': 180}, 'players': [{'x': 790, 'y': 170}, {'x': 20, 'y': 150}]}
    while True:
        p, data = main_queue.get()
        if p == 'rooms':
            rooms = data
            # print('\033c')
            print("[0..9]: join game | n: new game | u: update | Esc: quit program", flush=True)
            for i, r in enumerate(rooms):
                print(str(i) + ' - ' + r['name'] + ' - ' + r['id'])
            
        elif p == 'key':
            if data == 'esc':
                if playing:
                    curses.endwin()
                break
            elif data.isdigit() and not playing:
                if (int(data) < 0) or (int(data) >= len(rooms)):
                    print('Invalid game number')
                    continue
                room = join(rooms[int(data)]['id'], login)
                if room != None:
                    if rooms_process != None:
                        with requests.get("https://" + host + "/game/close/" + login,
                        cert=(certfile, keyfile),
                        verify=False) as response:
                            if response.status_code != 200:
                                print("Request failed with status code:", response.status_code)
                                exit(1)
                        rooms_process.join()
                        rooms_process = None
                    pong_process = Process(target=run_pong_listener, args=(room,))
                    pong_process.start()
                    playing = True
            elif data == 'q':
                if playing:
                    curses.endwin()
                if pong_process != None:
                    with requests.get("https://" + host + "/pong/close/" + room['id'] + '/' + room['player_id'],
                    cert=(certfile, keyfile),
                    verify=False) as response:
                        if response.status_code != 200:
                            print("Request failed with status code:", response.status_code)
                            exit(1)
                    pong_process.join()
                    pong_process = None
                    playing = False
                    with requests.get("https://" + host + "/game/need_update",
                        cert=(certfile, keyfile),
                        verify=False) as response:
                        next
                if rooms_process == None:
                    rooms_process = Process(target=run_rooms_listener)
                    rooms_process.start()
            elif data == 'ctrl':
                if pong_process != None:
                    with requests.get("https://" + host + "/pong/start/" + room['id'],
                    cert=(certfile, keyfile),
                    verify=False) as response:
                        next
            elif data == 'u':
                with requests.get("https://" + host + "/game/need_update",
                cert=(certfile, keyfile),
                verify=False) as response:
                    next
            elif data == 'n':
                room = new_game(login)
                if room != None:
                    if rooms_process != None:
                        with requests.get("https://" + host + "/game/close/" + login,
                        cert=(certfile, keyfile),
                        verify=False) as response:
                            if response.status_code != 200:
                                print("Request failed with status code:", response.status_code)
                                exit(1)
                        rooms_process.join()
                        rooms_process = None
                    pong_process = Process(target=run_pong_listener, args=(room,))
                    pong_process.start()
                    with requests.get("https://" + host + "/game/need_update",
                        cert=(certfile, keyfile),
                        verify=False) as response:
                        next
                    playing = True
            elif data in ['up', 'down', 'left', 'right'] and playing:
                with requests.get("https://" + host + "/pong/" + room['id'] + '/' + room['player_id'] + '/' + data,
                cert=(certfile, keyfile),
                verify=False) as response:
                    if response.status_code != 200:
                        print("Request failed with status code:", response.status_code)
                        exit(1)
        elif p == 'pong':
            if 'ball' in data.keys():
                draw_pong(room, data)
                playing = True
            elif 'score' in data.keys():
                score = data['score']
            elif 'team0' in data.keys():
                team0 = data['team0']
                team1 = data['team1']
    # 
    if rooms_process != None:
        with requests.get("https://" + host + "/game/close/" + login,
        cert=(certfile, keyfile),
        verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                exit(1)
        rooms_process.join()
    if pong_process != None:
        with requests.get("https://" + host + "/pong/close/" + room['id'] + '/' + room['player_id'],
        cert=(certfile, keyfile),
        verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                exit(1)
        pong_process.join()
        with requests.get("https://" + host + "/game/need_update",
            cert=(certfile, keyfile),
            verify=False) as response:
            next
    keys_process.join()
