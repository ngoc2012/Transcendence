from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import time
from random import randrange

online_players = {}
playings_players = {}
games = {}
game_id = 0
HEIGHT = 400
WIDTH = 800
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
RADIUS = 10
PADDLE_VITESSE = 5
PADDLE_DISTANCE = 20

def index(request):
	return (render(request, 'index.html'))

def home(request):
	return (render(request, 'home.html'))

def login(request):
	return (render(request, 'login.html'))

def pong(request):
	return (render(request, 'pong.html'))

def new_player(request):
    i = 0
    user_name = "user" + str(i)
    while (user_name in online_players.keys()):
        i += 1
        user_name = "user" + str(i)
    online_players[user_name] = {
            "online": time.time(),
            "invitations": {},
            "accepted": -1
            }
    print(online_players)
    return (JsonResponse({"user": user_name}))

def check_all_users_online():
    users = list(online_players.keys())
    for user in users:
        if time.time() - online_players[user]["online"] > 3:
            online_players.pop(user)

@csrf_exempt
def online_players_list(request): 
    #print(games)
    check_all_users_online()
    #print(request.POST)
    user = request.POST['user']
    users = list(online_players.keys())
    #print(user)
    #print(users)
    if user in users:
        online_players[user]["online"] = time.time()
        return (JsonResponse({
            "invitations": [v for k, v in online_players[user]["invitations"].items()],
            "online_players_list": users}))
    #print(online_players)
    return (JsonResponse({"invitations": [], "online_players_list": users}))

@csrf_exempt
def pong_state(request):
    #print(online_players)
    global online_players
    global games
    global WIDTH, HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_VITESSE, RADIUS
    #print(request.POST)
    g_id = int(request.POST['id'])
    if (g_id not in games.keys()):
        return (JsonResponse({"status": "error", "message": "Error: Game " + str(g_id) + " was not found."}))
    user = request.POST['user']
    if user not in games[g_id]["players"]:
        return (JsonResponse({"status": "error", "message": "Error: Player " + user + " was not found in the game."}))
    g = games[g_id]
    d = g["data"]
    i = g["order"][user]
    #if g["update"][i] == 1:
    #    return HttpResponse("wait")
    to_do = request.POST['do']
    if to_do == "up" and d["position"][i] > 0:
        d["position"][i] -= PADDLE_VITESSE
    elif to_do == "down" and d["position"][i] < HEIGHT - PADDLE_HEIGHT:
        d["position"][i] += PADDLE_VITESSE
    g["update"][i] = 1
    if g["status"] != "started":
        d["ball_y"] = d["position"][g["service"]] + PADDLE_HEIGHT / 2
        if d["x"][g["service"]] > WIDTH / 2:
            d["ball_x"] = d["x"][g["service"]] - RADIUS
        else:
            d["ball_x"] = d["x"][g["service"]] + PADDLE_WIDTH / 2 + RADIUS
    # new frame
    if g["status"] == "started" and sum(g["update"]) == g["n"]:
        g["update"] = [0 for i in range(g["n"])]
        d["ball_x"] += d["dx"]
        d["ball_y"] += d["dy"]
        # Bounce off the top and bottom walls
        if d["ball_y"] - RADIUS <= 0 or d["ball_y"] + RADIUS >= HEIGHT:
            d["dy"] = -d["dy"]
	    # Bounce off paddle
        print(d["ball_x"])
        if d["ball_x"] > WIDTH / 2:
            for i in range(g["n"]):
                if (d["x"][i] > WIDTH / 2 and
	                d["ball_x"] - RADIUS == d["x"][i] and
	                d["ball_y"] >= d["position"][i] and
                    d["ball_y"] <= d["position"][i] + PADDLE_HEIGHT):
	                d["dx"] = -d["dx"]
        else:
            for i in range(g["n"]):
                if (d["x"][i] < WIDTH / 2 and
	                d["ball_x"] + RADIUS == d["x"][i] + PADDLE_WIDTH and
	                d["ball_y"] >= d["position"][i] and
                    d["ball_y"] <= d["position"][i] + PADDLE_HEIGHT):
	                d["dx"] = -d["dx"]
	    # Check for game over
        if (d["ball_x"] - RADIUS < 0 or d["ball_x"] + RADIUS > WIDTH):
            if (d["ball_x"] - RADIUS < 0):
                for i, user in enumerate(games[g_id]["players"]):
                    if (d["x"][i] > WIDTH / 2):
                        g["point"][i] += 1
            else:
                for i, user in enumerate(games[g_id]["players"]):
                    if (d["x"][i] < WIDTH / 2):
                        g["point"][i] += 1
            g["service"] = (g["service"] + 1) % g["n"]
            if d["x"][g["service"]] > WIDTH / 2:
	            d["dx"] = -abs(d["dx"])
            else:
	            d["dx"] = abs(d["dx"])
            d["ball_y"] = d["position"][g["service"]] + PADDLE_HEIGHT / 2
            if d["x"][g["service"]] > WIDTH / 2:
                d["ball_x"] = d["x"][g["service"]] - RADIUS
            else:
                d["ball_x"] = d["x"][g["service"]] + PADDLE_WIDTH / 2 + RADIUS
            g["status"] = "end"
    return (JsonResponse({"status": "ok", "ball": {"x": d["ball_x"], "y": d["ball_y"]}, "position": d["position"], "point": g["point"]}))

@csrf_exempt
def start_game(request):
    global games
    global online_players
    #print(request.POST)
    g_id = int(request.POST['game_id'])
    #print(games)
    #print(games[g_id])
    if (g_id not in games.keys()):
        return HttpResponse("Game " + str(g_id) + " was not found.")
    user = request.POST['user']
    if (user not in games[g_id]["players"]):
        return HttpResponse("Player " + user + " was not found in the game.")
    games[g_id]["status"] = "started"
    return (HttpResponse("started"))

@csrf_exempt
def invite(request):
    #print(online_players)
    #print(request.POST)
    global game_id
    global online_players
    global games
    global WIDTH, HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_VITESSE, RADIUS
    players = request.POST.getlist('players[]')
    print(players)
    for user in players:
        if (user not in online_players.keys()):
            #print(user)
            #print(online_players.keys())
            return HttpResponse("Player " + user + " is not online.")
    game_id += 1
    games[game_id] = {
        "id": game_id,
        "game": request.POST['game'],
        "status": "waiting",
        "players": players,
        "n": len(players),
        "order": {},
        "host": request.POST['host'],
        "accepted": [request.POST['host']],
        "update": [0 for i in range(len(players))],
        "point": [0 for i in range(len(players))],
        "service": 0,
        "data": 
        {
            "height": HEIGHT,
            "width": WIDTH,
            "paddle_width": PADDLE_WIDTH,
            "paddle_height": PADDLE_HEIGHT,
            "ball_x": PADDLE_WIDTH + RADIUS,
            "ball_y": HEIGHT / 2,
            "ball_r": 10,
            "x": [0 for i in range(len(players))],
            "dx": 5,
            "dy": 5,
            "position": [HEIGHT /2 - PADDLE_HEIGHT / 2 for i in range(len(players))],
            "side": [i % 2 for i in range(len(players))],
            "update": [0 for i in range(len(players))],
        }
    }
    g = games[game_id]
    for i, user in enumerate(players):
        if (i % 2 == 0):
            g["data"]["x"][i] = i / 2 * PADDLE_DISTANCE
        else:
            g["data"]["x"][i] = WIDTH - (int(i / 2) * PADDLE_DISTANCE + PADDLE_WIDTH)
        g["order"][user] = i
        online_players[user]['invitations'][game_id] = g
    if (randrange(2) == 0):
        g["data"]["dy"] = 5
    else:
        g["data"]["dy"] = -5
    print(games)
    return (JsonResponse(g))

@csrf_exempt
def accept_invitation(request):
    global games
    global online_players
    print(request.POST)
    g_id = int(request.POST['game_id'])
    print(games)
    print(games[g_id])
    if (g_id not in games.keys()):
        return HttpResponse("Game " + str(g_id) + " was not found.")
    user = request.POST['user']
    if (user not in games[g_id]["players"]):
        return HttpResponse("Player " + user + " was not found in the game.")
    if (online_players[user]['accepted'] != -1):
        return HttpResponse("Player " + user + " was in another game.")
    online_players[user]["accepted"] = g_id
    if (user not in games[g_id]["accepted"]):
        games[g_id]["accepted"].append(user)
        if (len(games[g_id]["accepted"]) == len(games[g_id]["players"])):
            games[g_id]["status"] = "playing"
    return (JsonResponse(games[g_id]))

@csrf_exempt
def cancel_invitation(request):
    global games
    print(request.POST)
    g_id = int(request.POST['game_id'])
    if (g_id not in games.keys()):
        return HttpResponse("Game " + str(g_id) + " was not found.")
    user = request.POST['user']
    if (user not in games[g_id]["players"]):
        return HttpResponse("Player " + user + " was not found in the game.")
    if (online_players[user]["accepted"] == g_id):
        online_players[user]["accepted"] = -1
    for user in games[g_id]["players"]:
        if g_id in online_players[user]["invitations"].keys():
            online_players[user]["invitations"].pop(g_id)
    games.pop(g_id)
    return (HttpResponse("canceled"))

@csrf_exempt
def check_game_status(request):
    global games
    #print(request.POST)
    g_id = int(request.POST['game_id'])
    user = request.POST['user']
    users = list(online_players.keys())
    if user in users:
        online_players[user]["online"] = time.time()
    if (g_id not in games.keys()):
        return (HttpResponse("canceled"))
    return (JsonResponse(games[g_id]))
