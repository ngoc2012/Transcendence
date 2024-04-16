from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from game.models import TournamentModel, TournamentMatchModel, RoomsModel
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
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout
from django.core.cache import cache

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
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            decoded_refresh = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_refresh.get('user_id')
            User = get_user_model()
            user = User.objects.get(id=user_id)
            if user and jwt.decode(user.ref, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"]) == decoded_refresh:
                access_token, refresh_token = generate_jwt_tokens(user.id)
                user.acc = access_token
                user.ref = refresh_token

                ws_token = user.generate_ws_token()
                enable2fa = request.POST.get('enable2fa', 'false') == 'true'
                user.secret_2fa = pyotp.random_base32() if enable2fa else ''
                user.save()
                cache.delete(f'user_{user.id}')

                response_data = {
                    "validSession": True,
                    'login': user.username,
                    'name': user.name,
                    'email': user.email,
                    'enable2fa': enable2fa,
                    'ws': ws_token
                }
                response = JsonResponse(response_data)
                response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
                response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
                return response
        except jwt.ExpiredSignatureError:
            return JsonResponse({"validSession": False, "message": "Token expired."}, status=200)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return JsonResponse({"validSession": False, "message": "Invalid session."}, status=200)
        except Exception as e:
            return JsonResponse({"validSession": False, "message": str(e)}, status=200)
        return JsonResponse({"validSession": False, "message": "Invalid or mismatched token."}, status=200)
    else:
        return JsonResponse({"validSession": False, "message": "No Authorization token provided."}, status=200)


def tournament_history(request):
    try:
        response = requests.get("http://blockchain:9000/tournament_history")
        response.raise_for_status()

        data = response.json()
        tournament_names = data.get('names', [])
        return render(request, 'tournament_history.html', {'names' : tournament_names})

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tournament history: {e}")
        context = {'error_message': 'Failed to retrieve tournament history.'}
        return render(request, 'tournament_history.html', context)


@csrf_exempt
def get_tournament_data(request):
    try:
        tournament_name = request.GET.get('name')        
        if not tournament_name:
            return JsonResponse({"error": "Tournament name is required"}, status=400)
        url = f"http://blockchain:9000/tournaments/{tournament_name}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def display_2fa(request):

    email = request.POST['email']
    secret = request.POST['secret']
    # response = requests.get("http://blockchain:9000/print_me")
    # data = response.json()
    # print("data est egal a = ", data)
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

def tournament_local(request):
    return (render(request, 'tournament_local.html'))

def tournament_local_start(request):
    return (render(request, 'tournament_local_start.html'))

def generate_jwt_tokens(user_id):
    access_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(pytz.utc) + timedelta(minutes=5)
    }, JWT_SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(pytz.utc) + timedelta(days=7)
    }, JWT_REFRESH_SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token  

def new_player(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    required_fields = ['login', 'email', 'password', 'name']
    missing_fields = [field for field in required_fields if field not in request.POST or not request.POST[field]]
    if missing_fields:
        return JsonResponse({'error': f'Error: Missing field(s): {", ".join(missing_fields)}'}, status=400)

    try:
        User = get_user_model()

        user = User.objects.create_user(
            username=request.POST['login'],
            email=request.POST['email'],
            password=request.POST['password'],
            name=request.POST.get('name'),
        )

        access_token, refresh_token = generate_jwt_tokens(user.id)
        user.acc = access_token
        user.ref = refresh_token

        ws_token = user.generate_ws_token()
        enable2fa = request.POST.get('enable2fa', 'false') == 'true'
        user.secret_2fa = pyotp.random_base32() if enable2fa else ''
        user.save()
        
        response_data = {
            'login': user.username,
            'name': user.name,
            'email': user.email,
            'secret': user.secret_2fa if enable2fa else None,
            'ws': ws_token
        }
        response = JsonResponse(response_data)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        return response

    except IntegrityError:
        return JsonResponse({'error': 'Error: Login or email not available.'}, status=409)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

def log_in(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    username = request.POST.get('login')
    password = request.POST.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'No login or password provided!'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        enable2fa = 'true' if getattr(user, 'secret_2fa', '') else 'false'

        access_token, refresh_token = generate_jwt_tokens(user.id)

        user.acc = access_token
        user.ref = refresh_token
        user.save()

        ws_token = user.generate_ws_token()

        response_data = {
            'login': user.username,
            'name': user.name,
            'email': user.email,
            'enable2fa': enable2fa,
            'ws': ws_token
        }
        response = JsonResponse(response_data)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        return response

    else:
        return JsonResponse({'error': 'Invalid login credentials!'}, status=401)


# callback function used to get the info from the 42 API
@csrf_exempt
def callback(request):
    code = request.GET.get('code')
    standard_headers = {'X-Internal-Request': 'true'}
    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'headers': standard_headers,
            'client_id': API_PUBLIC,
            'client_secret': API_SECRET,
            'code': code,
            'redirect_uri': 'https://127.0.0.1:8080/callback/',
        })

        token_data = token_response.json()
        print(token_data)
        access_token = token_data['access_token']

        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })

        user_data = user_response.json()

#       essayer de connecter sinon creer : 
        user = authenticate(username=user_data['login'], password='')

        if user is not None:
            enable2fa = 'true' if getattr(user, 'secret_2fa', '') else 'false'

            access_token, refresh_token = generate_jwt_tokens(user.id)

            user.acc = access_token
            user.ref = refresh_token
            user.save()

            ws_token = user.generate_ws_token()

            response = {
                'my42login': user.username,
                'my42name': user.name,
                'my42email': user.email,
                'my42enable2fa': enable2fa,
                'my42ws': ws_token
            }

            response = render(request, 'index.html', response)
            response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)

            return response

        User = get_user_model()
        user = User.objects.create_user(
            username=user_data['login'],
            email=user_data['email'],
            password='',
            name=user_data['usual_full_name'],
        )

        access_token, refresh_token = generate_jwt_tokens(user.id)
        user.acc = access_token
        user.ref = refresh_token

        ws_token = user.generate_ws_token()
        enable2fa = 'false'
        user.secret_2fa = pyotp.random_base32() if enable2fa else ''
        user.save()
        
        response = {
            'my42login': user.username,
            'my42name': user.name,
            'my42email': user.email,
            'my42enable2fa': enable2fa,
            'my42ws': ws_token
        }

        response = render(request, 'index.html', response)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)

        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")


def logout(request):
    print(request)
    user = request.user
    user.acc = ''
    user.ref = ''
    user.save()
    cache.delete(f'user_{user.id}')

    response = JsonResponse({'logout': 'success'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def verify_qrcode(request):
    input_code = request.POST.get('input_code')

    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    player = PlayersModel.objects.get(login=request.POST['login'])

    totp = pyotp.TOTP(player.secret_2fa)
    if totp.verify(input_code):
        return JsonResponse({'result': '1'})
    return JsonResponse({'result': '0'})

@require_POST
def new_tournament(request):
    name = request.POST.get('name')
    game = request.POST.get('game')
    local = request.POST.get('local')
    try:
        if TournamentModel.objects.filter(name=name).exists():
            return JsonResponse({'error': 'A tournament with the same name already exists'}, status=400)

        owner = PlayersModel.objects.get(username=request.user.username)
        tournament = TournamentModel.objects.create(name=name, game=game, owner=owner)
        tournament.participants.add(owner)
        tournament.save()

        if local == 'true':
            tournament.local = True
            tournament.save()

        url = f"http://blockchain:9000/add_tournament/{name}"
        response = requests.post(url)
        response.raise_for_status()

        player_data = {
            'id': owner.id,
            'login': owner.login,
            'elo': owner.elo,
        }
        url = f"http://blockchain:9000/add_player/"
        data = {"name": name, "player": player_data}
        response = requests.post(url, json=data)
        response.raise_for_status()

        return JsonResponse({'message': 'Tournament created successfully', 'id': str(tournament.id), 'local': tournament.local, 'name': tournament.name}, status=200)
    except requests.exceptions.RequestException as e:
        print(f"Error calling add_tournament_route: {e}")
        return JsonResponse({'error': 'Failed to interact with blockchain'}, status=500)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Owner not found'}, status=404)
    except IntegrityError as e:
        return JsonResponse({'error': 'Tournament could not be created'}, status=409)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    

