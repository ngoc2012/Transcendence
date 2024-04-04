from flask import Flask
from flask import request

# Create an instance of the Flask class
app = Flask(__name__)

# Define a route for the root URL ("/")
@app.route("/ai/")
def hello():
    print("Hello, Flask!")
    # HTML content to be returned
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello Flask</title>
    </head>
    <body>
        <h1>Hello, Flask!</h1>
        <p>This is a simple Flask web application.</p>
    </body>
    </html>
    """
    return html_content

import sys
from multiprocessing import Process

def ai_listener(room_id, player_id):
    print(f"AI process started for room {room_id} and player {player_id}.")
    next
    # error = None
    # if request.method == 'POST':
    #     if valid_login(request.form['username'],
    #                    request.form['password']):
    #         return log_the_user_in(request.form['username'])
    #     else:
    #         error = 'Invalid username/password'
    # # the code below is executed if the request method
    # # was GET or the credentials were invalid
    # return render_template('login.html', error=error)
    
    # uri = "wss://django:8000/ws/pong/" + room['id'] + '/' + room['player_id'] + '/'
    # print(f"Connecting to {uri}...")

    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context.load_verify_locations(certfile)
    # ssl_context.load_cert_chain(certfile, keyfile=keyfile)

    # try:
    #     async with websockets.connect(uri, ssl=ssl_context) as pong_socket:
    #         while True:
    #             response_text = await pong_socket.recv()
    #             response = json.loads(response_text)
    #             if 'type' in response.keys():
    #                 if response['type'] == 'close' and response['player_id'] == room['player_id']:
    #                     break
    #                 elif response['type'] == 'start':
    #                     await pong_socket.send('start')
    #             main_queue.put(('pong', response))
    #         # print("Pong listener close")
    #         # await pong_socket.close()
    # except ws_exceptions.ConnectionClosedOK:
    #     print("Connection closed gracefully.")
    # except ws_exceptions.ConnectionClosedError as e:
    #     print(f"Connection closed with error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    # finally:
    #     print("Pong websocket connection closed.")
    print(f"AI process ended for room {room_id} and player {player_id}.")

@app.route('/ai/new', methods=['POST', 'GET'])
def new():
    
    room_id = request.form.get('room_id')
    player_id = request.form.get('player_id')
    sys.stderr.write("Start AI process\n")
    ai_process = Process(target=ai_listener, args=(room_id, player_id))
    ai_process.start()
    return "new/" + str(room_id) + "/" + str(player_id)

@app.route('/ai/del', methods=['POST', 'GET'])
def delete():
    return "del/"


# Run the application if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
