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
standard_headers = {'X-Internal-Request': 'true'}

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
            await rooms_socket.close()
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Rooms websocket connection closed.")

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
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Pong websocket connection closed.")

import keyboard
def keyboard_listener():
    global main_queue
    while True:
        key_event = keyboard.read_event(suppress=True)
        if key_event.event_type == keyboard.KEY_DOWN:
            key = key_event.name
            main_queue.put(('key', key))
            if key == 'esc':
                break

import getpass
def log_in():
    global login, name
    login = input("Login: ")
    password = getpass.getpass("Password: ")
    try:
        with requests.post("https://" + host + "/log_in/",
            data={"login": login, "password": password},
            headers=standard_headers,
            cert=(certfile, keyfile),
            verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
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
            headers=standard_headers,
            cert=(certfile, keyfile),
            verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
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

import signal
def signal_handler(signal, frame):
    exit(0)

import sys
import re
from multiprocessing import Process

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 CLI.py <ip> <port> ...")
        sys.exit(1)
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", sys.argv[1]):
        print("Invalid IP address")
        sys.exit(1)
    port_number = int(sys.argv[2])
    if port_number < 0 or port_number > 65535:
        print("Invalid port number")
        sys.exit(1)
    host = sys.argv[1] + ":" + sys.argv[2]
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

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    rooms_process = Process(target=run_rooms_listener)
    rooms_process.start()

    keys_process = Process(target=keyboard_listener)
    keys_process.start()

    pong_process = None
    rooms = []
    room = None
    playing = False

    while True:
        p, data = main_queue.get()
        if p == 'rooms':
            rooms = data
            print("[0..9]: join game | n: new game | u: update | Esc: quit program")
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
                                          headers=standard_headers,
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
            elif data == 'x':
                if playing:
                    curses.endwin()
                if pong_process != None:
                    with requests.get("https://" + host + "/pong/close/" + room['id'] + '/' + room['player_id'],
                                      headers=standard_headers,
                                      cert=(certfile, keyfile),
                                      verify=False) as response:
                        if response.status_code != 200:
                            print("Request failed with status code:", response.status_code)
                            exit(1)
                    pong_process.join()
                    pong_process = None
                    playing = False
                    with requests.get("https://" + host + "/game/need_update",
                                      headers=standard_headers,
                                      cert=(certfile, keyfile),
                                      verify=False) as response:
                        next
                if rooms_process == None:
                    rooms_process = Process(target=run_rooms_listener)
                    rooms_process.start()
            elif data == 'ctrl':
                if pong_process != None:
                    with requests.get("https://" + host + "/pong/start/" + room['id'],
                                      headers=standard_headers,
                                      cert=(certfile, keyfile),
                                      verify=False) as response:
                        next
            elif data == 'u':
                with requests.get("https://" + host + "/game/need_update",
                                  headers=standard_headers,
                                  cert=(certfile, keyfile),
                                  verify=False) as response:
                    next
            elif data == 'n':
                room = new_game(login)
                if room != None:
                    if rooms_process != None:
                        with requests.get("https://" + host + "/game/close/" + login,
                                          headers=standard_headers,
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
                                      headers=standard_headers,
                                      cert=(certfile, keyfile),
                                      verify=False) as response:
                        next
                    playing = True
            elif data in ['up', 'down', 'left', 'right'] and playing:
                with requests.get("https://" + host + "/pong/" + room['id'] + '/' + room['player_id'] + '/' + data,
                                  headers=standard_headers,
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
    if rooms_process != None:
        with requests.get("https://" + host + "/game/close/" + login,
                          headers=standard_headers,
                          cert=(certfile, keyfile),
                          verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                exit(1)
        rooms_process.join()
    if pong_process != None:
        with requests.get("https://" + host + "/pong/close/" + room['id'] + '/' + room['player_id'],
                          headers=standard_headers,
                          cert=(certfile, keyfile),
                          verify=False) as response:
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                exit(1)
        pong_process.join()
        with requests.get("https://" + host + "/game/need_update",
                          headers=standard_headers,
                          cert=(certfile, keyfile),
                          verify=False) as response:
            next
    keys_process.join()
