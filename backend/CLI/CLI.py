import requests
import json
import asyncio
import ssl
import sys
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
websocket = None

async def websocket_listener():
    global disconnect, mutex, websocket
    uri = "wss://" + host + "/ws/game/rooms/"  # Replace with the WebSocket server URI
    print(f"Connecting to {uri}...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(certfile)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("Connected to the WebSocket server.")
            while True:
                response = await websocket.recv()
                print(f"Received: {response}")
                # if disconnect:
                #     break
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

async def on_key_press(key):
    global disconnect
    print(f"Key pressed: {key}")
    if key == "q":
        print("Exiting...")
        with mutex:
            disconnect = True

async def keyboard_listener():
    global disconnect
    await asyncio.sleep(1) 

    while True:
        key = input("Press 'q' to exit: ")
        await on_key_press(key)
        with mutex:
            if disconnect:
                print("Disconnect flag set. Breaking loop.")
                await websocket.send("exit")
                break

async def main():
    # tasks = [websocket_listener(), keyboard_listener()]
    # tasks = [websocket_listener()]
    tasks = [keyboard_listener(), websocket_listener()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
