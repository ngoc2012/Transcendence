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
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.contrib.auth.hashers import make_password, check_password
import random, string
from accounts.models import CustomUser
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login

API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')


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

# create a new player in the database and his 2fa key used for authenticator


def tournament(request):
     return (render(request, 'tournament.html'))

def tournament_lobby(request):
     return (render(request, 'tournament_lobby.html'))

def tournament_start(request, tournament_id):
     return (render(request, 'tournament_start.html'))

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
    try:
        user = CustomUser.objects.create_user(request.POST['login'], request.POST['email'], request.POST['password'])
        user.name = request.POST['name']
        user.save
    except IntegrityError:
         return HttpResponse("Error: login or email not available.")
    
    bool = request.POST['enable2fa']
    if (bool == 'true'):
        mysecret = pyotp.random_base32()
    else:
        mysecret = ''
    user.secret_2fa = mysecret
    user.save

    #JWT handling
    access_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, JWT_SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user.id
    }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')
    response = JsonResponse({
        'access_token': access_token,
        'login': user.username,
        'name': user.name,
        'email': user.email,
        'secret': user.secret_2fa
    })
    response.set_cookie('refresh_token', refresh_token, httponly=True)
    return response


# Login an user and set JWT token
@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'No login or password!'}, status=400)

        player = authenticate(request, username=username, password=password)
        if player:
            enable2fa = 'true' if getattr(player, 'secret_2fa', '') != '' else 'false'
            auth_login(request, player)
            response = JsonResponse({
                # 'access_token': '',
                'login': getattr(player, 'username', ''),
                'name': getattr(player, 'name', ''),
                'email': getattr(player, 'email', ''),
                'enable2fa': enable2fa
            })
            return response
        else:
            return JsonResponse({'error': 'Invalid login credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Invalid request type'}, status=400)

    #         # JWT handling
    #         if check_password(password, player.password):
    #             access_token = jwt.encode({
    #                 'user_id': player.id,
    #                 'exp': datetime.utcnow() + timedelta(hours=1)
    #             }, JWT_SECRET_KEY, algorithm='HS256')
    #             refresh_token = jwt.encode({
    #                 'user_id': player.id
    #             }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')

    #             response = JsonResponse({
    #                 'access_token': access_token,
    #                 'login': player.login,
    #                 'name': player.name,
    #                 'email': player.email,
    #                 'enable2fa': enable2fa
    #             })
    #             response.set_cookie('refresh_token', refresh_token, httponly=True)
    #             return response
    #         else:
    #             return JsonResponse({'error': 'Password not correct!'}, status=401)
    #     except PlayersModel.DoesNotExist:
    #         return JsonResponse({'error': 'Login does not exist!'}, status=404)
    # else:
    #     return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


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
        if request.user.is_authenticated:
             print('auth ok')
    #     try:
    #         tournament = TournamentModel.objects.create(name=name, game=game, owner=owner)
    #         player = PlayersModel.objects.get(login=login)
    #         tournament.participants.add(player)
    #         return JsonResponse({'message': 'Tournament created successfully', 'id': str(tournament.id)}, status=200)
    #     except Exception as e:
    #         return JsonResponse({'error': str(e)}, status=400)
    # else:
    #      return JsonResponse({'error': 'Invalid request'}, status=405)