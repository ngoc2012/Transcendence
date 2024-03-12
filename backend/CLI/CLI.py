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
disconnect = False
quit_game = False
rooms_socket = None
pong_socket = None
rooms = []
login = None
tasks = None

async def rooms_listener():
    global disconnect, mutex, rooms_socket, rooms
    uri = "wss://" + host + "/ws/game/rooms/"
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as rooms_socket:
            while True:
                response = await rooms_socket.recv()
                obj = json.loads(response)
                print('\033c')
                if isinstance(obj, list):
                    rooms = obj
                    for i in rooms:
                        print(str(i) + ' - ' + i['name'] + ' - ' + i['id'])
                print("[0..9]: join game\nn: new game\nq: quit")
                with mutex:
                    if disconnect:
                        break
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("WebSocket connection closed.")
        with mutex:
            disconnect = True

async def pong_listener(room):
    global disconnect, mutex, pong_socket
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
                print("[0..9]: join game\nn: new game\nq: quit")
                print(obj)
                with mutex:
                    if quit_game:
                        break
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("WebSocket connection closed.")
        with mutex:
            quit_game = True

async def join(game):
    global login, rooms
    if game + 1 > len(rooms):
        return
    try:
        response = requests.post("https://" + host + "/game/join",
            data={"login": login, "game_id": rooms[game]['id']}, 
            cert=(certfile, keyfile),
            verify=False)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            return
        await asyncio.create_task(pong_listener(response))
    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return

async def number_keyboard():
    game = -1
    for i in range(10):
        if keyboard.is_pressed(str(i)):
            return i
    return game

import keyboard
async def keyboard_listener():
    global disconnect, mutex, rooms_socket, quit_game
    # await asyncio.sleep(0.1)
    asyncio.create_task(rooms_listener())
    while True:
        # game = number_keyboard()
        if keyboard.is_pressed('0'):
            join(0)
        elif keyboard.is_pressed('esc') or keyboard.is_pressed('x'):
            with mutex:
                disconnect = True
                await rooms_socket.send("exit")
                break
        elif keyboard.is_pressed('q'):
            with mutex:
                quit_game = True
                await pong_socket.send("exit")
                break
        elif keyboard.is_pressed('up'):
            print("Up arrow key is pressed.")
        elif keyboard.is_pressed('down'):
            print("Down arrow key is pressed.")
        elif keyboard.is_pressed('left'):
            print("Left arrow key is pressed.")
        elif keyboard.is_pressed('right'):
            print("Right arrow key is pressed.")
        else:
            await asyncio.sleep(0.1)
        with mutex:
            if disconnect == True:
                break

async def main():
    await asyncio.create_task(keyboard_listener())
    # tasks = [keyboard_listener(), rooms_listener()]
    # await asyncio.gather(*tasks)

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
