from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel, TournamentModel, TournamentMatchModel, RoomsModel, PlayerRoomModel
from django.utils import timezone
from transchat.models import Room
from django.shortcuts import redirect
from django.conf import settings
import requests
import secrets
import os
import pyotp
import random
import jwt
import json
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.contrib.auth.hashers import make_password, check_password
import random, string
from web3 import Web3
from django.contrib.auth import logout


API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')

ganache_url = 'http://ganache:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))



def fill_Tournament_Data():
    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        accounts = web3.eth.accounts
        chosen_account = accounts[0]

        tournament_name = "MyTournament"
        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            TournamentRegistry.functions.addTournament(tournament_name).transact({'from': chosen_account})
            tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        players = [
            {'name': 'Player1', 'elo': 1500},
            {'name': 'Player2', 'elo': 1600},
            {'name': 'Player3', 'elo': 1550},
            {'name': 'Player4', 'elo': 1580}
        ]
        for player_data in players:
            TournamentRegistry.functions.addPlayer(tournament_index, player_data['name'], player_data['elo']).transact({'from': chosen_account})

        matches = [
            {'player1': {'name': 'Player3', 'elo': 1550}, 'player2': {'name': 'Player4', 'elo': 1580}, 'scorePlayer1': 1, 'scorePlayer2': 0, 'round': 'Semi-Final', 'winner': 'Player3'},
            {'player1': {'name': 'Player1', 'elo': 1500}, 'player2': {'name': 'Player2', 'elo': 1600}, 'scorePlayer1': 2, 'scorePlayer2': 1, 'round': 'Final', 'winner': 'Player1'}
        ]
        for match_data in matches:
            player1 = match_data['player1']
            player2 = match_data['player2']
            TournamentRegistry.functions.addMatch(tournament_index,
                                                   player1['name'], 
                                                   player2['name'],
                                                   match_data['scorePlayer1'], 
                                                   match_data['scorePlayer2'],
                                                   match_data['round'], 
                                                   match_data['winner']).transact({'from': chosen_account})

        tournament_winner = "Player1"
        TournamentRegistry.functions.setTournamentWinner(tournament_index, tournament_winner).transact({'from': chosen_account})

        TournamentRegistry.functions.setTournamentPending(tournament_index, False).transact({'from': chosen_account})

    except Exception as e:
        print("Error:", e)
        return -1


def get_tournament_data(request):
    try:
        tournament_name = request.GET.get('name')
        print("mon tournoi = ", tournament_name)
        
        if not tournament_name:
            return JsonResponse({"error": "Tournament name is required"}, status=400)



        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)


        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            return JsonResponse({"error": "Tournament not found."}, status=400)
        

        contenders = TournamentRegistry.functions.getContenders(tournament_index).call()

        #     # player_data est un tuple (name, elo)
        #     name = player_data[0]  # Accéder au nom du joueur
        #     elo = player_data[1]   # Accéder au elo du joueur
        #     print("Player:")
        #     print("Name:", name, "| Elo:", elo)
            

        # print("Matches in order:")
        matches = TournamentRegistry.functions.getMatches(tournament_index).call()

        #     player1 = match[0]
        #     player2 = match[1]
        #     score1 = match[2]
        #     score2 = match[3]
        #     round_name = match[4]
        #     winner = match[5]
        #     print("Match:")
        #     print("Round:", round_name)
        #     print("Player 1:", player1, "| Score:", score1)
        #     print("Player 2:", player2, "| Score:", score2)
        #     print("Winner:", winner)
        
        tournament_winner = TournamentRegistry.functions.getTournamentWinner(tournament_index).call()
        is_pending = TournamentRegistry.functions.isTournamentPending(tournament_index).call()
        

        data = {
            'tournament_name': tournament_name,
            'tournament_winner': tournament_winner,
            'is_pending': is_pending,
            'contenders': contenders,
            'matches': matches
        }




        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def print_Tournament_Data():
    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)

        tournament_name = "MyTournament"
        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            print("Tournament not found.")
            return -1

        print("Tournament Name:", tournament_name)
        print("Contenders:")

        contenders = TournamentRegistry.functions.getContenders(tournament_index).call()

        for player_data in contenders:
            name = player_data[0]
            elo = player_data[1]
            print("Player:")
            print("Name:", name, "| Elo:", elo)
            

        print("Matches in order:")
        matches = TournamentRegistry.functions.getMatches(tournament_index).call()

        for match in matches:
            player1 = match[0]
            player2 = match[1]
            score1 = match[2]
            score2 = match[3]
            round_name = match[4]
            winner = match[5]
            print("Match:")
            print("Round:", round_name)
            print("Player 1:", player1, "| Score:", score1)
            print("Player 2:", player2, "| Score:", score2)
            print("Winner:", winner)
        
        tournament_winner = TournamentRegistry.functions.getTournamentWinner(tournament_index).call()
        is_pending = TournamentRegistry.functions.isTournamentPending(tournament_index).call()
        
        print("Tournament Winner:", tournament_winner)
        print("Is Pending:", is_pending)

        print("Tournament data printed successfully.")
        return 1
    except Exception as e:
        print("Error:", e)
        return -1








def tournament_history(request):

    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        tournament_names = TournamentRegistry.functions.getTournamentNames().call()

        return render(request, 'tournament_history.html', {'names' : tournament_names})

    except Exception as e:
        print("Error:", e)
        return -1





def redirect(request):
	return (render(request, 'index.html'))

def index(request):
	return (render(request, 'index.html'))

def lobby(request):
	return (render(request, 'lobby.html'))

def signup(request):
    return render(request, 'signup.html')

def login(request):
	return (render(request, 'login.html'))

def twofa(request):
    return (render(request, 'twofa.html'))

def code_2fa(request):
    return (render(request, 'code_2fa.html'))

@csrf_exempt
def display_2fa(request):
    email = request.POST['email']
    secret = request.POST['secret']
    fill_Tournament_Data()
    print_Tournament_Data()
    return render(request, 'display_2fa.html', {'email': email, 'secret_key': secret})


def qrcode_2fa(request):
	return (render(request, 'qrcode_2fa.html'))


# use sendgrid API to send an email to the user containing the code used for the 2fa
@csrf_exempt
def mail_2fa(request):
    sender_email = EMAIL_SENDER
    recipient_email = request.GET.get('email')
    print(recipient_email)
    code = ""
    for _ in range(6):
        digit = random.randint(0, 9)
        code += str(digit)
    settings.CODE = code
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject='2FA CODE TRANSCENDENCE',
        html_content=code)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print('Email sent successfully')
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print('Error sending email:', str(e))
    return JsonResponse({'code': code})

# verify the email code
@csrf_exempt
def verify(request):
    input_code = request.POST.get('input_code')
    if(input_code == settings.CODE):
        return JsonResponse({'result': '1'})
    return JsonResponse({'result': '0'})


def tournament(request):
     return (render(request, 'tournament.html'))

def tournament_lobby(request):
     return (render(request, 'tournament_lobby.html'))

def tournament_start(request, tournament_id):
     return (render(request, 'tournament_start.html'))



# create a new player in the database and his 2fa key used for authenticator

@csrf_exempt
def new_player(request):
    if 'login' not in request.POST or request.POST['login'] == "":
        return HttpResponse("Error: No login!")
    if 'email' not in request.POST or request.POST['email'] == "":
        return HttpResponse("Error: No email!")
    if 'password' not in request.POST or request.POST['password'] == "":
        return HttpResponse("Error: No password!")
    if 'name' not in request.POST or request.POST['name'] == "":
        return HttpResponse("Error: No name!")
    if PlayersModel.objects.filter(login=request.POST['login']).exists():
        return HttpResponse("Error: Login '" + request.POST['login'] + "' exist.")
    bool = request.POST['enable2fa']
    if (bool == 'true'):
        mysecret = pyotp.random_base32()
    else:
        mysecret = ''

    hashed_password = make_password(request.POST['password'])

    new_player = PlayersModel(
        login=request.POST['login'],
        password=hashed_password,
        name=request.POST['name'],
        email=request.POST['email'],
        secret_2fa = mysecret
    )
    new_player.save()

    current_time = datetime.now(timezone.utc)
    expiration_time = current_time + timedelta(hours=1)
    #JWT handling
    access_token = jwt.encode({
        'user_id': new_player.id,
        'exp': expiration_time
    }, JWT_SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': new_player.id
    }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')
    response = JsonResponse({
        'access_token': access_token,
        'login': new_player.login,
        'name': new_player.name,
        'email': new_player.email,
        'secret': new_player.secret_2fa
    })
    response.set_cookie('refresh_token', refresh_token, httponly=True)
    # send_login(new_player.login, new_player.id)

    return response

# Login an user and set JWT token
@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        if 'login' not in request.POST:
            return JsonResponse({'error': 'No login!'}, status=400)
        if 'password' not in request.POST:
            return JsonResponse({'error': 'No password!'}, status=400)

        login = request.POST['login']
        password = request.POST['password']

        try:
            player = PlayersModel.objects.get(login=login)
            if (player.secret_2fa != ''):
                enable2fa = 'true'
            else:
                enable2fa = 'false'

            current_time = datetime.now(timezone.utc)
            expiration_time = current_time + timedelta(hours=1)

            # JWT handling
            if check_password(password, player.password):
                access_token = jwt.encode({
                    'user_id': player.id,
                    'exp': expiration_time
                }, JWT_SECRET_KEY, algorithm='HS256')
                refresh_token = jwt.encode({
                    'user_id': player.id
                }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')

                response = JsonResponse({
                    'access_token': access_token,
                    'login': player.login,
                    'name': player.name,
                    'email': player.email,
                    'enable2fa': enable2fa
                })
                response.set_cookie('refresh_token', refresh_token, httponly=True)
                return response
            else:
                return JsonResponse({'error': 'Password not correct!'}, status=401)
        except PlayersModel.DoesNotExist:
            return JsonResponse({'error': 'Login does not exist!'}, status=404)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# callback function used to get the info from the 42 API
@csrf_exempt
def callback(request):
    code = request.GET.get('code')
    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': API_PUBLIC,
            'client_secret': API_SECRET,
            'code': code,
            'redirect_uri': 'https://127.0.0.1:8080/callback/',
        })

        token_data = token_response.json()
        access_token = token_data['access_token']

        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })

        user_data = user_response.json()
        hashed_password = make_password('password')
        if not PlayersModel.objects.filter(login=user_data['login']).exists():
            new_player = PlayersModel(
                login=user_data['login'],
                password=hashed_password,
                name=user_data['usual_full_name'],
                email=user_data['email'],
                secret_2fa=''
            )
            new_player.save()

        player = PlayersModel.objects.get(login=user_data['login'])

        # JWT handling
        access_token_jwt = jwt.encode({
            'user_id': player.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, JWT_SECRET_KEY, algorithm='HS256')

        refresh_token_jwt = jwt.encode({
            'user_id': player.id
        }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')

        response = render(request, 'index.html', {
            'my42login': user_data['login'],
            'my42name': user_data['usual_full_name'],
            'my42email': user_data['email'],
            'my42JWT': access_token_jwt
        })
        response.set_cookie('refresh_token', refresh_token_jwt, httponly=True)

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")

@csrf_exempt
def verify_qrcode(request):
    input_code = request.POST.get('input_code')

    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    player = PlayersModel.objects.get(login=request.POST['login'])

    totp = pyotp.TOTP(player.secret_2fa)
    if totp.verify(input_code):
        return JsonResponse({'result': '1'})
    return JsonResponse({'result': '0'})


@csrf_exempt
def new_tournament(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        game = request.POST.get('game')
        login = request.POST.get('login')
        owner = PlayersModel.objects.get(login=request.POST['login'])
        try:
            tournament = TournamentModel.objects.create(name=name, game=game, owner=owner)
            player = PlayersModel.objects.get(login=login)
            tournament.participants.add(player)
            return JsonResponse({'message': 'Tournament created successfully', 'id': str(tournament.id)}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
         return JsonResponse({'error': 'Invalid request'}, status=405)
