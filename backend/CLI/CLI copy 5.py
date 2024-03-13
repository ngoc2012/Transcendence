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

import threading
mutex = threading.Lock()

quit_program = False
quit_lobby = False
quit_game = False

rooms_socket = None
pong_socket = None

login = None
rooms = []
tasks = None

async def rooms_listener():
    global quit_program, mutex, rooms_socket, rooms, quit_lobby
    uri = "wss://" + host + "/ws/game/rooms/"
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as rooms_socket:
            while True:
                # print('\033c')
                listener = keyboard.Listener(
                    on_press=on_press,
                    on_release=on_release)
                listener.start()
                print("listener keyboard starts")
                response = await rooms_socket.recv()
                obj = json.loads(response)
                
                if isinstance(obj, list):
                    rooms = obj
                    for i, r in enumerate(rooms):
                        print(str(i) + ' - ' + r['name'] + ' - ' + r['id'])
                print("[0..9]: join game\nn: new game\nEsc: quit")
                with mutex:
                    if quit_lobby:
                        rooms_socket = None
                        break
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
        with mutex:
            quit_program = True
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
        with mutex:
            quit_program = True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        with mutex:
            quit_program = True
    finally:
        print("Rooms websocket connection closed.")
        with mutex:
            quit_lobby = True
            rooms_socket = None

async def pong_listener(room):
    global quit_game, mutex, pong_socket

    if pong_socket != None:
        return
    
    if "error" in room.lower():
        print(room)
        return
    
    room = json.loads(room)
    
    uri = "wss://" + host + "/ws/pong/" + room['id'] + '/' + room['player_id'] + '/'
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as pong_socket:
            while True:
                response = await pong_socket.recv()
                obj = json.loads(response)
                print('\033c')
                print("q: quit")
                print(obj)
                with mutex:
                    if quit_game:
                        pong_socket = None
                        break
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Pong websocket connection closed.")
        with mutex:
            pong_socket = None
            quit_game = True

def join(game):
    print("join")
    global login, rooms, quit_game
    if game + 1 > len(rooms):
        return
    try:
        response = requests.post("https://" + host + "/game/join",
            data={"login": login, "game_id": rooms[game]['id']}, 
            cert=(certfile, keyfile),
            verify=False)
        # print(response)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            return
        with mutex:
            quit_game = False
        asyncio.create_task(pong_listener(response.text))
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return

def lobby():
    global mutex, quit_lobby
    with mutex:
        quit_lobby = False
    asyncio.create_task(rooms_listener())

# import keyboard
# async def keyboard_listener():
#     global quit_program, mutex, rooms_socket, quit_lobby, pong_socket, quit_game
#     await lobby()
#     await asyncio.sleep(0.1)
#     while True:
#         print("keyboard")
#         # game = number_keyboard()
#         game = -1
#         for i in range(10):
#             if keyboard.is_pressed(str(i)):
#                 game = i
#         # print()
#         if game != -1:
#             await join(game)
#         elif keyboard.is_pressed('esc'):
#             with mutex:
#                 quit_lobby = True
#                 quit_game = True
#             if rooms_socket != None:
#                 await rooms_socket.send("exit")
#             if pong_socket != None:
#                 await pong_socket.send("exit")
#             print("Bye")
#             break
#         elif keyboard.is_pressed('q'):
#             with mutex:
#                 quit_game = True
#             if pong_socket != None:
#                 await pong_socket.send("exit")
#             if rooms_socket == None:
#                 await lobby()
#         elif keyboard.is_pressed('up'):
#             if pong_socket != None:
#                 await pong_socket.send('up')
#         elif keyboard.is_pressed('down'):
#             if pong_socket != None:
#                 await pong_socket.send('down')
#         elif keyboard.is_pressed('left'):
#             if pong_socket != None:
#                 await pong_socket.send('left')
#         elif keyboard.is_pressed('right'):
#             if pong_socket != None:
#                 await pong_socket.send('right')
#         else:
#             await asyncio.sleep(0.1)
#         with mutex:
#             if quit_program:
#                 break

def on_press(key):
    print("key press")
    global quit_program, mutex, rooms_socket, quit_lobby, pong_socket, quit_game
    try:
        key_char = key.char
    except AttributeError:
        key_char = key.name
    print(key_char)
    if key_char.isdigit():
        join(int(key_char))
    elif key_char == 'esc':
        with mutex:
            quit_lobby = True
            quit_game = True
        if rooms_socket is not None:
            rooms_socket.send("exit")
        if pong_socket is not None:
            pong_socket.send("exit")
        print("Bye")
        exit(0)
    elif key_char == 'q':
        with mutex:
            quit_game = True
        if pong_socket is not None:
            pong_socket.send("exit")
        if rooms_socket is None:
            lobby()
    elif key_char in ['up', 'down', 'left', 'right']:
        if pong_socket is not None:
            pong_socket.send(key_char)

def on_release():
    print("key release")

from pynput import keyboard
async def main():
    global  quit_lobby
    # await asyncio.create_task(keyboard_listener())
    with mutex:
        quit_lobby = False
    await rooms_listener()

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

if __name__ == "__main__":
    # log_in()
    asyncio.run(main())
