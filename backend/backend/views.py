from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from game.models import TournamentModel, TournamentMatchModel, RoomsModel
from accounts.models import PlayersModel
from accounts.forms import UploadFileForm
from django.utils import timezone
from transchat.models import Room
from django.shortcuts import redirect
import json
from django.conf import settings
import requests, pyotp, secrets, os, random, jwt, string, pytz, uuid
from urllib.parse import quote
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

def tournament(request):
    return (render(request, 'tournament.html'))

def tournament_local(request):
    return (render(request, 'tournament_local.html'))

def tournament_local_start(request):
    return (render(request, 'tournament_local_start.html'))

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

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
                user.save()
                cache.delete(f'user_{user.id}')

                response_data = {
                    "validSession": True,
                    'login': user.username,
                    'name': user.name,
                    'email': user.email,
                    'enable2fa': enable2fa,
                    'ws': ws_token,
                    'avatar': user.avatar.url
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

@csrf_exempt
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
        enable2fa = request.POST.get('enable2fa')
        if (enable2fa == 'false'):
            enable2fa = ''
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

@csrf_exempt
def log_in(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    username = request.POST.get('login')
    password = request.POST.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'No login or password provided!'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        print(user.secret_2fa)
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
            'ws': ws_token,
            'avatar': user.avatar.url
        }
        response = JsonResponse(response_data)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        return response

    else:
        return JsonResponse({'error': 'Invalid login credentials!'}, status=401)


def login42(request):
    try:
        state = uuid.uuid4().hex
        request.session['oauth_state_login'] = state

        client_id = 'u-s4t2ud-bda043967d92d434d1d6c24cf1d236ce0c6cc9c718a9198973efd9c5236038ed'
        redirect_uri = quote('https://127.0.0.1:8080/callback/')
        authorize_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}'

        return JsonResponse({'url': authorize_url})
    
    except KeyError as e:
        return JsonResponse({'error': f'Missing key in request: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

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
                'my42ws': ws_token,
                'avatar': user.avatar.url
            }

            response = render(request, 'index.html', response)
            response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
            cache.delete(f'user_{user.id}')
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
            'my42ws': ws_token,
            'avatar': user.avatar.url
        }
        cache.delete(f'user_{user.id}')
        response = render(request, 'index.html', response)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)

        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")


def logout(request):
    user = request.user
    user.acc = ''
    user.ref = ''
    user.save()
    cache.delete(f'user_{user.id}')

    response = JsonResponse({'logout': 'success'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('sessionid')
    return response


def verify_qrcode(request):
    input_code = request.POST.get('input_code')

    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    player = PlayersModel.objects.get(login=request.POST['login'])
    print(player.login)
    print(player.secret_2fa)
    print(input_code)
    totp = pyotp.TOTP(player.secret_2fa)
    if totp.verify(input_code):
        return JsonResponse({'result': '1'})
    return JsonResponse({'result': '0'})

@csrf_exempt
def profile(request, username):
    if request.method == 'POST':
        if request.POST['requester'] and request.POST['user']:
            print("requester qnd user")
            if request.POST['requester'] == request.POST['user']:
                print("request != user")
                user = PlayersModel.objects.filter(login=username).get(login=username)
                context = {
                    'ownprofile': True,
                    'id': user.id,
                    'login': user.login,
                    'password': user.password,
                    'name': user.name,
                    'alias': user.tourn_alias,
                    'history': user.history.all(),
                    'email': user.email,
                    'elo': user.elo,
                    'friends': user.friends.all(),
                    'url': user.avatar.url,
                    'form': UploadFileForm()
                }
                return render(request, 'profile.html', context)
            else:
                user = PlayersModel.objects.filter(login=username).get(login=username)
                context = {
                    'ownprofile': False,
                    'id': user.id,
                    'login': user.login,
                    'password': user.password,
                    'name': user.name,
                    'alias': user.tourn_alias,
                    'history': user.history.all(),
                    'email': user.email,
                    'elo': user.elo,
                    'friends': user.friends.all(),
                    'url': user.avatar.url,
                    'form': UploadFileForm()
                }
                return render(request, 'profile.html', context)
    elif request.GET['requester'] and request.GET['user']:
        if request.GET['requester'] == request.GET['user']:
            user = PlayersModel.objects.filter(login=username).get(login=username)
            context = {
                'ownprofile': True,
                'id': user.id,
                'login': user.login,
                'password': user.password,
                'name': user.name,
                'alias': user.tourn_alias,
                'history': user.history.all(),
                'email': user.email,
                'elo': user.elo,
                'friends': user.friends.all(),
                'url': user.avatar.url,
                'form': UploadFileForm()
            }
            return render(request, 'profile.html', context)
        else:
            user = PlayersModel.objects.filter(login=username).get(login=username)
            context = {
                'ownprofile': False,
                'id': user.id,
                'login': user.login,
                'password': user.password,
                'name': user.name,
                'alias': user.tourn_alias,
                'history': user.history.all(),
                'email': user.email,
                'elo': user.elo,
                'friends': user.friends.all(),
                'url': user.avatar.url,
                'form': UploadFileForm()
            }
            return render(request, 'profile.html', context)
    else:
        user = PlayersModel.objects.filter(login=username).get(login=username)
        context = {
            'ownprofile': True,
            'id': user.id,
            'login': user.login,
            'password': user.password,
            'name': user.name,
            'alias': user.tourn_alias,
            'history': user.history.all(),
            'email': user.email,
            'elo': user.elo,
            'friends': user.friends.all(),
            'url': user.avatar.url,
            'form': UploadFileForm()
        }
        return render(request, 'profile.html', context)

@csrf_exempt
def alias(request, username):
    user = PlayersModel.objects.filter(login=username).get(login=username)
    if request.method == 'GET':
        return(render(request, 'alias.html'))
    if request.method == 'POST':
        if 'alias' in request.POST:
            try:
                check_alias = PlayersModel.objects.get(tourn_alias=request.POST['alias'])
            except PlayersModel.DoesNotExist:
                user.tourn_alias = request.POST['alias']
                user.save()
                return HttpResponse('Tournament alias succesfully changed')
            response = HttpResponse('Alias already in use')
            response.status_code = 401
            return response
        
@csrf_exempt
def password(request, username):
    user= PlayersModel.objects.filter(login=username).get(login=username)
    if request.method == 'POST':
        if 'oldpwd' in request.POST and 'newpwd' in request.POST:
            oldpwd = request.POST['oldpwd']
            newpwd = request.POST['newpwd']
            if check_password(oldpwd, user.password) == True:
                new = make_password(newpwd)
                user.password = new
                user.save()
                response = HttpResponse('Password changed succesfully')
                response.status_code = 200
                return response
            else:
                response = HttpResponse('Incorrect password')
                response.status_code = 401
                return response
    return render(request, 'change_password.html')

@csrf_exempt
def email(request, username):
    user = PlayersModel.objects.filter(login=username).get(login=username)
    if request.method == 'POST':
        if 'password' in request.POST:
            if check_password(request.POST['password'], user.password) == False:
                response = HttpResponse('Invalid password')
                response.status_code = 401
                return response
            else:
                user.email = request.POST['email']
                user.save()
                response = HttpResponse('Email changed succesfully')
                response.status_code = 200
                return response
    return render(request, 'change_email.html')

@csrf_exempt
def change_login(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        if check_password(request.POST['password'], user.password) == False:
            response = HttpResponse('Invalid password.')
            response.status_code = 401
            return response
        try:
            check_login = PlayersModel.objects.get(login=request.POST['new_login'])
        except PlayersModel.DoesNotExist:
            new_username = request.POST['new_login']
            user.login = new_username
            user.username = new_username
            user.save()
            response = HttpResponse('Login changed succesfully')
            response.status_code = 200
            return response
        response = HttpResponse('Login not available')
        response.status_code = 401
        return response
    return render(request, 'change_login.html')

@csrf_exempt
def name(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        if check_password(request.POST['password'], user.password) == False:
            response = HttpResponse('Invalid password')
            response.status_code = 401
            return response
        user.name = request.POST['name']
        user.save()
        response = HttpResponse('Name changed succesfully')
        response.status_code = 200
        return response
    return render(request, 'change_name.html')

@csrf_exempt
def friend(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        if request.POST['type'] == 'send':
            if request.POST['friend'] == username:
                response = HttpResponse('You cannnot be friend with yourself')
                response.status_code = 403
                return response
            try:
                new_friend = PlayersModel.objects.get(login=request.POST['friend'])
            except PlayersModel.DoesNotExist:
                response = HttpResponse(request.POST['friend'] + ' does not exist')
                response.status_code = 404
                return response
            try:
                friend_exist = user.friends.get(login=request.POST['friend'])
            except PlayersModel.DoesNotExist:
                response = HttpResponse('Friend request sent to ' + request.POST['friend'])
                response.status_code = 200
                return response
            response = HttpResponse('You are already friend with ' + request.POST['friend'])
            response.status_code = 401
            return response
        if request.POST['type'] == 'receive':
            if request.POST['response'] == 'accept':
                sender = PlayersModel.objects.get(login=request.POST['sender'])
                if request.POST['friend']:
                    friend = PlayersModel.objects.get(login=request.POST['friend'])
                sender.friends.add(friend)
                friend.friends.add(sender)
                sender.save()
                friend.save()
                response = HttpResponse('You accepted ' + request.POST['sender'] + ' friend request. You are now friends.')
                response.status_code = 200
                return response
            if request.POST['response'] == 'decline':
                sender = PlayersModel.objects.get(login=request.POST['sender'])
                response = HttpResponse('You declined ' + request.POST['sender'] + ' friend request.')
                response.status_code = 200
                return response
    return render(request, 'add_friend.html')

@csrf_exempt
def avatar(request, username):
    user = PlayersModel.objects.get(login=username)
    print(request)
    form = UploadFileForm(request.POST, request.FILES)
    print(request.POST)
    print(request.FILES)
    if form.is_valid():
        user.avatar = request.FILES['file']
        user.save()
        return redirect(request)
    return redirect(request)
    

@require_POST
def new_tournament(request):
    name = request.POST.get('name')
    try:
        if TournamentModel.objects.filter(name=name).exists():
            return JsonResponse({'error': 'A tournament with the same name already exists'}, status=400)
        else:
            print(request.user)
            owner = request.user
            tournament = TournamentModel.objects.create(name=name, game='pong', owner=owner, newRound=True, local=True)
            tournament.participants.add(owner)
            tournament.save()

        return JsonResponse({'message': 'Tournament OK', 'local': True, 'name': name, 'id':tournament.id}, status=200)
    except IntegrityError as e:
        return JsonResponse({'error': 'Tournament could not be created'}, status=409)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def auth_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    username = request.POST.get('login')
    password = request.POST.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'No login or password provided!'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        enable2fa = 'true' if getattr(user, 'secret_2fa', '') else 'false'

        response_data = {
            'login': user.username,
            'name': user.name,
            'email': user.email,
            'enable2fa': enable2fa,
        }
        response = JsonResponse(response_data)
        return response
    else:
        return JsonResponse({'error': 'Invalid login credentials!'}, status=401)

