from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from game.models import TournamentModel, TournamentMatchModel, RoomsModel
from accounts.models import PlayersModel
from accounts.forms import UploadFileForm, PlayerChangeNameForm, PlayerChangeLoginForm, PlayerChangeEmailForm, PlayerChangeAliasForm, PlayerChangePasswordForm, PlayerAddFriendForm
from django.utils import timezone
from transchat.models import Room
import json
from django.shortcuts import redirect
from django.urls import reverse
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
from cryptography.fernet import Fernet
from .validation import NewPlayerForm, TournamentNameForm, verifyQrCodeForm, verifyLoginForm, verifyCodeForm
from django.db import transaction
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')


ENCRYPT_KEY = os.environ.get('ENCRYPT_KEY')

def encrypt(message):
  try:
    fernet = Fernet(ENCRYPT_KEY)
    encrypted_text = fernet.encrypt(message.encode()).decode()
    return encrypted_text
  except Exception as e:
    return None

def decrypt(encrypted_text):
  try:
    fernet = Fernet(ENCRYPT_KEY)
    decrypted_text = fernet.decrypt(encrypted_text.encode()).decode()
    return decrypted_text
  except Exception as e:
    return None

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
    return JsonResponse({'csrftoken': get_token(request)})

@csrf_protect
def display_2fa(request):

    email = request.POST['email']
    secret = request.POST['secret']

    return render(request, 'display_2fa.html', {'email': email, 'secret_key': decrypt(secret)})

def qrcode_2fa(request):
	return (render(request, 'qrcode_2fa.html'))

def invalid_session():
    response = JsonResponse({"validSession": False, "message": "Token expired."}, status=200)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('sessionid')
    response.delete_cookie('login42')
    return response

def validate_session(request):
    access_token = request.COOKIES.get('access_token')
    if not access_token:
        return JsonResponse({"validSession": False, "message": "No Authorization token provided."}, status=200)

    jti = None

    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        if not jti or cache.get(jti):
            return invalid_session()

        user = User.objects.filter(id=payload.get('user_id')).first()
        if not user:
            return invalid_session()

        ws_token = user.generate_ws_token()
        enable2fa = request.POST.get('enable2fa', 'false') == 'true'
        user.save()

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
        # response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        # response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        return response

    except jwt.ExpiredSignatureError:
        return invalid_session()
    except jwt.InvalidTokenError:
        return invalid_session()


def tournament_history(request):
    try:
        response = requests.get("http://blockchain:9000/tournament_history")
        response.raise_for_status()

        data = response.json()
        tournament_names = data.get('names', [])
        return render(request, 'tournament_history.html', {'names' : tournament_names})

    except requests.exceptions.RequestException as e:
        context = {'error_message': 'Failed to retrieve tournament history.'}
        return render(request, 'tournament_history.html', context)


@csrf_protect
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
        return JsonResponse({"error": str(e)}, status=400)

# use sendgrid API to send an email to the user containing the code used for the 2fa
@csrf_protect
def mail_2fa(request):
    sender_email = EMAIL_SENDER
    recipient_email = request.GET.get('email')
    code = ""
    for _ in range(6):
        digit = random.randint(0, 9)
        code += str(digit)
    settings.CODE = code
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject='TRANSCENDENCE 2FA VERIFICATION CODE',
        html_content=code)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        pass
    return JsonResponse({'code': code})

# verify the email code
@csrf_protect
def verify(request):
    form = verifyCodeForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    input_code = form.cleaned_data['input_code']

    if (input_code == int(settings.CODE)):
        return JsonResponse({'result': '1'}, status=200)
    return JsonResponse({'result': '0'}, status=400)

def generate_jwt_tokens(user_id):
    access_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(pytz.utc) + timedelta(minutes=60),
        'jti': str(uuid.uuid4())
    }, settings.JWT_SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(pytz.utc) + timedelta(minutes=120),
        'jti': str(uuid.uuid4())
    }, settings.JWT_REFRESH_SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token

@csrf_exempt
def np(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    form = NewPlayerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors.as_json()}, status=400)

    try:
        User = get_user_model()
        user_data = form.cleaned_data
        user = User.objects.create_user(
            username=user_data['login'],
            email=user_data['email'],
            password=user_data['password'],
            name=user_data.get('name', '')
        )

        access_token, refresh_token = generate_jwt_tokens(user.id)

        ws_token = user.generate_ws_token()
        enable2fa = request.POST.get('enable2fa', '')
        temp_secret = pyotp.random_base32() if enable2fa != 'false' else ''
        hashed_secret = encrypt(temp_secret) if enable2fa != 'false' else ''

        user.secret_2fa = hashed_secret
        user.save()
        authenticate(username=user.username, password=user.password)

        response_data = {
            'login': user.username,
            'name': user.name,
            'email': user.email,
            'secret': user.secret_2fa if enable2fa != 'false' else None,
            'ws': ws_token
        }
        response = JsonResponse(response_data)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        response.delete_cookie('login42')
        return response

    except IntegrityError:
        return JsonResponse({'error': 'Error: Login or email not available.'}, status=409)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=400)


    except IntegrityError:
        return JsonResponse({'error': 'Error: Login or email not available.'}, status=409)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=400)

@csrf_protect
def new_player(request):
   return  np(request)

@csrf_protect
def auth_view(request):
    form = verifyLoginForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    username = form.cleaned_data['login']
    password = form.cleaned_data['password']

    user = authenticate(request, login=username, password=password)
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


@csrf_exempt
def lg(request):
    form = verifyLoginForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    username = form.cleaned_data['login']
    password = form.cleaned_data['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        enable2fa = 'true' if getattr(user, 'secret_2fa', '') else 'false'
        access_token, refresh_token = generate_jwt_tokens(user.id)

        user.save()

        ws_token = user.generate_ws_token()
        response_data = {
            'login': user.username,
            'name': user.name,
            'email': user.email,
            'enable2fa': enable2fa,
            'ws': ws_token,
            'avatar': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None
        }
        response = JsonResponse(response_data)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        response.delete_cookie('login42')

        return response
    else:
        return JsonResponse({'error': 'Invalid login credentials!'}, status=401)

@csrf_protect
def log_in(request):
    return lg(request)

@csrf_protect
def login42(request):
    try:
        state = uuid.uuid4().hex
        request.session['oauth_state_login'] = state

        client_id = API_PUBLIC
        redirect_uri = quote('https://127.0.0.1:8080/callback/')
        authorize_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}'

        return JsonResponse({'url': authorize_url})

    except KeyError as e:
        return JsonResponse({'error': f'Missing key in request: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)

# callback function used to get the info from the 42 API
@csrf_protect
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
            user.save()

            ws_token = user.generate_ws_token()

            response = {
                'my42login': user.username,
                'my42name': user.name,
                'my42email': user.email,
                'my42enable2fa': enable2fa,
                'my42ws': ws_token,
                'my42avatar': user.avatar.url,
            }

            response = render(request, 'index.html', response)
            response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
            response.set_cookie('login42', secure=True)
            response.delete_cookie('sessionid')

            return response

        User = get_user_model()
        user = User.objects.create_user(
            username=user_data['login'],
            email=user_data['email'],
            password='',
            name=user_data['usual_full_name'],
        )

        access_token, refresh_token = generate_jwt_tokens(user.id)

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
            'my42avatar': user.avatar.url
        }

        response = render(request, 'index.html', response)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', secure=True)
        response.set_cookie('login42', secure=True)
        response.delete_cookie('sessionid')

        return response
    except Exception as e:
        if 'duplicate key value violates unique constraint "accounts_playersmodel_username_key"' in str(e):
                response = {
                    'error_user': "Login already taken",
                }
                response = render(request, 'index.html', response)
                return response
        else:
            return render(request, 'index.html', {'error_user': "An error occured"})


@csrf_protect
def logout(request):
    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')

    if access_token:
        revoke_token(access_token, settings.JWT_SECRET_KEY)
    if refresh_token:
        revoke_token(refresh_token, settings.JWT_REFRESH_SECRET_KEY)

    response = JsonResponse({'logout': 'success'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('sessionid')
    response.delete_cookie('login42')
    return response

def revoke_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        jti = decoded.get("jti")
        if jti:
            cache.set(jti, "revoked", timeout=None)
    except jwt.ExpiredSignatureError:
        pass
    except jwt.InvalidTokenError:
        pass

def verify_qrcode(request):
    form = verifyQrCodeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    input_code = form.cleaned_data['input_code']
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    player = PlayersModel.objects.get(login=request.POST['login'])
    totp = pyotp.TOTP(decrypt(player.secret_2fa))
    if totp.verify(input_code):
        return JsonResponse({'result': '1'}, status=200)
    return JsonResponse({'result': '0', 'error': 'Invalid OTP code'}, status=400)

@csrf_protect
def profile(request, username):
    if request.method == 'POST':
        if 'requester' in request.POST and 'user' in request.POST:
            if request.POST['requester'] == request.POST['user']:
                try:
                    user = PlayersModel.objects.filter(login=username).get(login=username)
                except PlayersModel.DoesNotExist:
                    response = HttpResponse("User not found")
                    response.status_code = 404
                    return response
                context = {
                    'ownprofile': True,
                    'isfriend': False,
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
                try:
                    user = PlayersModel.objects.filter(login=username).get(login=username)
                except PlayersModel.DoesNotExist:
                    response = HttpResponse("User not found")
                    response.status_code = 404
                    return response
                try:
                    friend = PlayersModel.objects.get(login=username).friends.get(login=request.POST['request'])
                except PlayersModel.DoesNotExist:
                    context = {
                        'ownprofile': False,
                        'isfriend': False,
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
                context = {
                    'ownprofile': False,
                    'isfriend': True,
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
    elif 'requester' in request.GET and 'user' in request.GET:
        if request.GET['requester'] == request.GET['user']:
            try:
                user = PlayersModel.objects.filter(login=username).get(login=username)
            except PlayersModel.DoesNotExist:
                response = HttpResponse("User not found")
                response.status_code = 404
                return response
            context = {
                'ownprofile': True,
                'isfriend': False,
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
            try:
                user = PlayersModel.objects.filter(login=username).get(login=username)
            except PlayersModel.DoesNotExist:
                response = HttpResponse("User not found")
                response.status_code = 404
                return response
            try:
                friend = PlayersModel.objects.get(login=username).friends.get(login=request.GET['requester'])
            except PlayersModel.DoesNotExist:
                context = {
                    'ownprofile': False,
                    'isfriend': False,
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
            context = {
                'ownprofile': False,
                'isfriend': True,
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
        try:
            user = PlayersModel.objects.filter(login=username).get(login=username)
        except PlayersModel.DoesNotExist:
            response = HttpResponse("User not found")
            response.status_code = 404
            return response
        context = {
            'ownprofile': True,
            'isfriend': False,
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

@csrf_protect
def alias(request, username):
    user = PlayersModel.objects.filter(login=username).get(login=username)
    if request.method == 'POST':
        if 'type' in request.POST:
            user.tourn_alias = ''
            user.save()
            response = HttpResponse("Tournament alias deleted")
            response.status_code = 200
            return response

        form = PlayerChangeAliasForm(request.POST)
        if form.is_valid():
            if request.POST['alias'] != '' :
                try:
                    check_alias = PlayersModel.objects.get(tourn_alias=form.cleaned_data['alias'])
                except PlayersModel.DoesNotExist:
                    user.tourn_alias = form.cleaned_data['alias']
                    user.save()
                    return HttpResponse('Tournament alias succesfully changed')
                response = HttpResponse('Alias already in use')
                response.status_code = 401
            else:
                response = HttpResponse("You must enter a value")
                response.status_code = 403
                return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return(render(request, 'alias.html'))

@csrf_protect
def password(request, username):
    User = get_user_model()
    user = User.objects.get(login=username)
    if request.method == 'POST':
        form = PlayerChangePasswordForm(request.POST)
        if form.is_valid():
            if check_password(form.cleaned_data['oldpwd'], user.password):
                with transaction.atomic():
                    user.set_password(form.cleaned_data['newpwd'])
                    user.save()
                    user.refresh_from_db()
                response = HttpResponse('Password changed successfully')
                response.status_code = 200

                return response
            else:
                response = HttpResponse('Incorrect password')
                response.status_code = 401
                return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return render(request, 'change_password.html')

@csrf_protect
def email(request, username):
    user = PlayersModel.objects.filter(login=username).get(login=username)
    if request.method == 'POST':
        form = PlayerChangeEmailForm(request.POST)
        if form.is_valid():
            if not check_password(form.cleaned_data['password'], user.password):
                response = HttpResponse('Invalid password')
                response.status_code = 401
                return response
            new_email = form.cleaned_data['email']
            if PlayersModel.objects.filter(email=new_email).exists():
                response = HttpResponse('Email already in use')
                response.status_code = 409
                return response
            user.email = new_email
            user.save()
            response = HttpResponse('Email changed successfully')
            response.status_code = 200

            return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return render(request, 'change_email.html')

@csrf_protect
def change_login(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        form = PlayerChangeLoginForm(request.POST)
        if form.is_valid():
            if check_password(form.cleaned_data['password'], user.password) == False:
                response = HttpResponse('Invalid password.')
                response.status_code = 401
                return response
            try:
                check_login = PlayersModel.objects.get(login=form.cleaned_data['new_login'])
            except PlayersModel.DoesNotExist:
                user.login = form.cleaned_data['new_login']
                user.username = form.cleaned_data['new_login']
                user.save()

                response = HttpResponse('Login changed succesfully')
                response.status_code = 200
                return response
            response = HttpResponse('Login not available')
            response.status_code = 401
            return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return render(request, 'change_login.html')

@csrf_protect
def name(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        form = PlayerChangeNameForm(request.POST)
        if form.is_valid():
            if check_password(form.cleaned_data['password'], user.password) == False:
                response = HttpResponse('Invalid password')
                response.status_code = 401
                return response
            user.name = form.cleaned_data['name']
            user.save()
            response = HttpResponse('Name changed succesfully')
            response.status_code = 200

            return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return render(request, 'change_name.html')

@csrf_protect
def friend(request, username):
    user = PlayersModel.objects.get(login=username)
    if request.method == 'POST':
        if request.POST['type'] == 'info':
            try:
                friend = user.friends.get(login=request.POST['friend'])
            except PlayersModel.DoesNotExist:
                response = HttpResponse("false")
                response.status_code = 200
                return response
            response = HttpResponse("True")
            response.status_code = 200
            return response
        form = PlayerAddFriendForm(request.POST)
        if form.is_valid():
            if request.POST['type'] == 'send':
                if form.cleaned_data['friend'] == username:
                    response = HttpResponse('You cannnot be friend with yourself')
                    response.status_code = 403
                    return response
                try:
                    new_friend = PlayersModel.objects.get(login=form.cleaned_data['friend'])
                except PlayersModel.DoesNotExist:
                    response = HttpResponse(form.cleaned_data['friend'] + ' does not exist')
                    response.status_code = 404
                    return response
                try:
                    friend_exist = user.friends.get(login=form.cleaned_data['friend'])
                except PlayersModel.DoesNotExist:
                    response = HttpResponse('Friend request sent to ' + form.cleaned_data['friend'])
                    response.status_code = 200
                    return response
                response = HttpResponse('You are already friend with ' + form.cleaned_data['friend'])
                response.status_code = 401
                return response
            if request.POST['type'] == 'receive':
                if request.POST['response'] == 'accept':
                    sender = PlayersModel.objects.get(login=form.cleaned_data['sender'])
                    if form.cleaned_data['friend']:
                        friend = PlayersModel.objects.get(login=form.cleaned_data['friend'])
                    sender.friends.add(friend)
                    friend.friends.add(sender)
                    sender.save()
                    friend.save()
                    response = HttpResponse('You accepted ' + form.cleaned_data['sender'] + ' friend request. You are now friends.')
                    response.status_code = 200
                    return response
                if request.POST['response'] == 'decline':
                    sender = PlayersModel.objects.get(login=form.cleaned_data['sender'])
                    response = HttpResponse('You declined ' + form.cleaned_data['sender'] + ' friend request.')
                    response.status_code = 200
                    return response
        else:
            response = HttpResponse("Invalid data")
            response.status_code = 400
            return response
    return render(request, 'add_friend.html')

@csrf_protect
def avatar(request, username):
    user = PlayersModel.objects.get(login=username)

    user.avatar = request.FILES['id_file']
    user.save()
    return JsonResponse({"new_pp": True, "url": user.avatar.url})

def tournament_request(request):
    try:
        tournaments = TournamentModel.objects.filter(
            owner=request.user,
            terminated=False,
            ready=False
        )
        if tournaments.exists():
            for tournament in tournaments:
                url = f"http://blockchain:9000/delete_tournament/{tournament.name}"
                tournament.delete()

        tournament = TournamentModel.objects.filter(
            owner=request.user,
            terminated=False
        ).first()

        if not tournament:
            return JsonResponse({'status': 'not_found'}, status=200)

        if not tournament.ready:
            url = f"http://blockchain:9000/delete_tournament/{tournament.name}"
            tournament.delete()
            return JsonResponse({'status': 'not_found'}, status=200)

        return JsonResponse({
            'status': 'active',
            'local': True,
            'name': tournament.name,
            'id': tournament.id
        }, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=400)


@require_POST
def new_tournament(request):
    form = TournamentNameForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)

    name = form.cleaned_data['name']

    try:
        if TournamentModel.objects.filter(name=name).exists():
            return JsonResponse({'error': 'A tournament with the same name already exists'}, status=400)
        else:
            owner = request.user
            tournament = TournamentModel.objects.create(name=name, game='pong', owner=owner, newRound=True, local=True)
            tournament.participants.add(owner)
            tournament.save()

        return JsonResponse({'message': 'Tournament OK', 'local': True, 'name': name, 'id': str(tournament.id)}, status=200)
    except IntegrityError as e:
        return JsonResponse({'error': 'Tournament could not be created'}, status=409)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
