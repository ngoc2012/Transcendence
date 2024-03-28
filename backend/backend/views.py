from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import TournamentModel, TournamentMatchModel, RoomsModel, PlayerRoomModel
from accounts.models import PlayersModel
from django.utils import timezone
from transchat.models import Room
from django.shortcuts import redirect
from django.conf import settings
import requests, pyotp, secrets, os, random, jwt, string, pytz
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login as auth_login, get_user_model

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

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def validate_session(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            user_id = payload['user_id']
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            if user:
                enable2fa = 'true' if getattr(user, 'secret_2fa', '') else 'false'
                return JsonResponse({
                    "validSession": True,
                    'login': user.username,
                    'name': user.name,
                    'email': user.email,
                    'enable2fa': enable2fa
                })
        except jwt.ExpiredSignatureError:
            return JsonResponse({"validSession": False, "message": "Token expired."}, status=401)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return JsonResponse({"validSession": False, "message": "Invalid session."}, status=401)
        except Exception as e:
            return JsonResponse({"validSession": False, "message": str(e)}, status=400)
    else:
        return JsonResponse({"validSession": False, "message": "No Authorization token provided."}, status=401)


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
     if request.user.is_authenticated:
        return (render(request, 'tournament.html'))
     return JsonResponse({'error': 'Login needed'}, status=401)

def tournament_lobby(request):
     return (render(request, 'tournament_lobby.html'))

def tournament_start(request, tournament_id):
     return (render(request, 'tournament_start.html'))

# @csrf_exempt
def new_player(request):
    required_fields = ['login', 'email', 'password', 'name']
    for field in required_fields:
        if field not in request.POST or not request.POST[field]:
            return JsonResponse({'error': f'Error: No {field}!'}, status=400)
    
    try:
        User = get_user_model()
        user = User.objects.create_user(
            username=request.POST['login'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        user.name = request.POST['name']

        enable2fa = request.POST.get('enable2fa', 'false') == 'true'
        user.secret_2fa = pyotp.random_base32() if enable2fa else ''
        user.save()

        # JWT handling
        access_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now(pytz.utc) + timedelta(hours=1)
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
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')
        return response

    except IntegrityError:
        return JsonResponse({'error': 'Error: Login or email not available.'}, status=409)


# Login an user and set JWT token
# @csrf_exempt
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'No login or password provided!'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            enable2fa = 'true' if getattr(user, 'secret_2fa', '') != '' else 'false'
            auth_login(request, user)

            # Create JWT tokens
            access_token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now(pytz.utc) + timedelta(hours=1)
            }, JWT_SECRET_KEY, algorithm='HS256')

            refresh_token = jwt.encode({
                'user_id': user.id
            }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')

            response = JsonResponse({
                'access_token': access_token,
                'login': user.username,
                'name': user.name,
                'email': user.email,
                'enable2fa': enable2fa
            })
            response.set_cookie('refresh_token', refresh_token, httponly=True)
            return response

        else:
            if username and not user:
                return JsonResponse({'error': 'Login does not exist!'}, status=404)
            else:
                return JsonResponse({'error': 'Password not correct!'}, status=401)
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
            'exp': datetime.now(pytz.utc) + timedelta(hours=1)
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


def new_tournament(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        game = request.POST.get('game')
        print(request.user.login)
        owner = PlayersModel.objects.get(username=request.user.login)
        try:
            tournament = TournamentModel.objects.create(name=name, game=game, owner=owner)
            tournament.participants.add(owner)
            tournament.save()
            return JsonResponse({'message': 'Tournament created successfully', 'id': str(tournament.id)}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
         return JsonResponse({'error': 'Invalid request'}, status=405)