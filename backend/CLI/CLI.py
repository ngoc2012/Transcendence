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

login = None
tasks = None

stop_event = asyncio.Event()
stop_event.clear()

async def rooms_listener():
    global host, stop_event, certfile, keyfile
    uri = "wss://" + host + "/ws/game/rooms/"
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as rooms_socket:
            while not stop_event.is_set():
                try:
                    response = await rooms_socket.recv()
                    obj = json.loads(response)
                    print('\033c')
                    if isinstance(obj, list):
                        rooms = obj
                        for i, r in enumerate(rooms):
                            print(str(i) + ' - ' + r['name'] + ' - ' + r['id'])
                    print("[0..9]: join game\nn: new game\nEsc: quit")
                except asyncio.TimeoutError:
                    if stop_event.is_set():
                        break
    except ws_exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except ws_exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Rooms websocket connection closed.")

import keyboard
def keyboard_listener():
    while True:
        key_event = keyboard.read_event(suppress=True)

        if key_event.event_type == keyboard.KEY_DOWN:
            key = key_event.name
            if key == 'enter':
                print('Enter is pressed')
            elif key == 'q' or key == 'esc':
                print('Quitting the program')
                stop_event.set()
                break
            elif key == 's':
                print('Skipping the things')
            # if key.isdigit():
            #     join(int(key))
            # elif key == 'esc':
            #     with mutex:
            #         quit_lobby = True
            #         quit_game = True
            #     if rooms_socket is not None:
            #         rooms_socket.send("exit")
            #     if pong_socket is not None:
            #         pong_socket.send("exit")
            #     print("Bye")
            #     exit(0)
            # elif key == 'q':
            #     with mutex:
            #         quit_game = True
            #     if pong_socket is not None:
            #         pong_socket.send("exit")
            #     if rooms_socket is None:
            #         lobby()
            # elif key in ['up', 'down', 'left', 'right']:
            #     if pong_socket is not None:
            #         pong_socket.send(key)

async def main():
    await asyncio.create_task(rooms_listener())

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

# import signal

# def signal_handler(signal, frame):
#     global stop_event
#     print("Received signal, exiting gracefully...")
#     # Set the stop_event flag to initiate a clean shutdown
#     stop_event.set()

from multiprocessing import Process
if __name__ == "__main__":
    # log_in()
    # Register the signal handler for SIGINT and SIGTERM
    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)
    p = Process(target=asyncio.run, args=(rooms_listener(),))
    p.start()
    keyboard_listener()
    stop_event.set()
    p.join()
