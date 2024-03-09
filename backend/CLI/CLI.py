import requests
import subprocess
import os
import sys
import urllib3
import json
# import getpass

# Disable SSL-related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import asyncio
import websockets
import keyboard
import ssl

host = "127.0.0.1:8080"
certfile = "minh-ngu.crt"
keyfile = "minh-ngu.key"

async def rooms_socket():
    uri = "wss://" + host + "/ws/game/rooms/"  # Replace with the WebSocket server URI
    print(f"Connecting to {uri}...")

    # Create an SSL context
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    # # Create a WebSocket SSL context
    # ws_ssl_context = websockets.ssl.WSContext(ssl_context)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            while True:
                message_to_send = input("Enter message (press 'q' to quit): ")
                await websocket.send(message_to_send)

                if message_to_send.lower() == 'q':
                    break

                response = await websocket.recv()
                print(f"Received: {response}")

    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("WebSocket connection closed.")


def main():
    
    if not os.path.exists(certfile) or not os.path.exists("minh-ngu.key"):
        try:
            result = subprocess.run("openssl req -newkey rsa:4096 -x509 -sha256 -days 365 \
                -nodes -out " + certfile + " -keyout " + keyfile + " \
                -subj \"/C=FR/ST=Paris/L=Paris/O=42 School/OU=minh-ngu/CN=minh-ngu/\"",
                shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("SSL certificate and key files generated successfully!")
        except subprocess.CalledProcessError as e:
            print("Failed to generate SSL certificate and key files. Error:", e)
            return 1

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
        return 1
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return 1
    # try:
    #     response = requests.get(host + "/game/update",
    #         cert=("minh-ngu.crt", "minh-ngu.key"), verify=False)
    #     if response.status_code != 200:
    #         print("Request failed with status code:", response.status_code)
    # except requests.exceptions.RequestException as e:  
    #     print("Request failed. Error:", e)
    #     return 1
    # rooms = json.loads(response.text)
    # print("Rooms: ", rooms)
    # Run the WebSocket client
    asyncio.get_event_loop().run_until_complete(rooms_socket())

if __name__ == "__main__":
    exit_code = main()
    os.remove(certfile)
    os.remove(keyfile)
    sys.exit(exit_code)