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
rooms_socket = None

async def rooms_listener():
    global disconnect, mutex, rooms_socket
    uri = "wss://" + host + "/ws/game/rooms/"  # Replace with the WebSocket server URI
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as rooms_socket:
            while True:
                response = await rooms_socket.recv()
                rooms = json.loads(response)
                print('\033c')
                if isinstance(rooms, list):
                    for i in rooms:
                        print(i['name'] + ' - ' + i['id'])
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

async def on_key_press(key):
    global disconnect, mutex, rooms_socket
    print(f"Key pressed: {key.name}")
    if key.name == "q":
        print("Exiting...")
        with mutex:
            disconnect = True
    else:
        await rooms_socket.send(key.name)

import keyboard
async def keyboard_listener():
    global disconnect, mutex, rooms_socket
    await asyncio.sleep(0.1)
    while True:
        if keyboard.is_pressed('q'):
            with mutex:
                disconnect = True
                await rooms_socket.send("exit")
                break
        else:
            await asyncio.sleep(0.1)
        with mutex:
            if disconnect == True:
                break

async def main():
    tasks = [keyboard_listener(), rooms_listener()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
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

    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        exit(1)
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        exit(1)
    asyncio.run(main())
