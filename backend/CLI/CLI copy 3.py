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
quit_input = False

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
                print("Waiting for message...")
                response = await rooms_socket.recv()
                obj = json.loads(response)
                print('\033c')
                if isinstance(obj, list):
                    with mutex:
                        rooms = obj
                    for i, r in enumerate(rooms):
                        print(str(i) + ' - ' + r['name'] + ' - ' + r['id'])
                print("[0..9]: join game\nn: new game\nEsc: quit")
                with mutex:
                    if quit_lobby:
                        rooms_socket = None
                        break
                await asyncio.sleep(0.1)
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
                        pong_socket = True
                        break
                await asyncio.sleep(0.1)
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Pong websocket connection closed.")
        with mutex:
            pong_socket = True
            quit_game = True

async def join(game):
    global login, rooms, quit_game
    if game + 1 > len(rooms):
        return
    try:
        response = requests.post("https://" + host + "/game/join",
            data={"login": login, "game_id": rooms[game]['id']}, 
            cert=(certfile, keyfile),
            verify=False)
        print(response)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            return
        with mutex:
            quit_game = False
        asyncio.create_task(pong_listener(json.loads(response)))
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return

async def lobby():
    print("lobby")
    global mutex, quit_lobby
    with mutex:
        quit_lobby = False
    asyncio.create_task(rooms_listener())

from pynput import keyboard as pynput_keyboard
def on_key_pressed(key):
    global quit_program, mutex, rooms_socket, quit_lobby, pong_socket, quit_game
    loop = asyncio.get_event_loop()

    def run_sync_code():
        global quit_program, mutex, rooms_socket, quit_lobby, pong_socket, quit_game
        try:
            key_char = key.char
        except AttributeError:
            key_char = key.name
        print(key_char)
        if key_char.isdigit():
            asyncio.create_task(join(int(key_char)))
        elif key_char == 'esc':
            with mutex:
                quit_lobby = True
                quit_game = True
            if rooms_socket is not None:
                loop.create_task(rooms_socket.send("exit"))
            if pong_socket is not None:
                loop.create_task(pong_socket.send("exit"))
            print("Bye")
            loop.stop()
        elif key_char == 'q':
            with mutex:
                quit_game = True
            if pong_socket is not None:
                loop.create_task(pong_socket.send("exit"))
            if rooms_socket is None:
                loop.create_task(lobby())
        elif key_char in ['up', 'down', 'left', 'right']:
            if pong_socket is not None:
                loop.create_task(pong_socket.send(key_char))

        with mutex:
            if quit_program:
                loop.stop()

    threading.Thread(target=run_sync_code).start()


# async def get_input():
#     # asyncio.create_task(keyboard_listener())
#     await keyboard_listener()

async def main():
    global quit_lobby
    # await lobby()
    with mutex:
        quit_lobby = False
    await asyncio.create_task(rooms_listener())
    # await asyncio.sleep(0.1)
    # await get_input()

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
    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    with pynput_keyboard.Listener(on_press=on_key_pressed) as listener:
        loop.run_forever()
