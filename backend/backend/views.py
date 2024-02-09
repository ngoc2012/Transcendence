from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel
from django.shortcuts import redirect
from django.conf import settings
import requests
import secrets
import os
import pyotp
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
GOOGLE_OAUTH2_PROJECT_ID = os.environ.get('GOOGLE_OAUTH2_PROJECT_ID')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')


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

# le mettre en retour de mail_2fa?
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
    mysecret = pyotp.random_base32()
    print('mysecret = ', mysecret)
    new_player = PlayersModel(
        login=request.POST['login'],
        password=request.POST['password'],
        name=request.POST['name'],
        email=request.POST['email'],
        secret_2fa = mysecret
    )
    new_player.save()
    return JsonResponse({
        'login': new_player.login,
        'name': new_player.name,
        'email': new_player.email,
        'secret': new_player.secret_2fa
    })


# login an user
@csrf_exempt
def log_in(request):
    if 'login' not in request.POST:
        return (HttpResponse("Error: No login!"))
    if 'password' not in request.POST:
        return (HttpResponse("Error: No password!"))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' does not exist!"))
    player = PlayersModel.objects.get(login=request.POST['login'])
    if player.password == request.POST['password']:
        return (JsonResponse({
            'login': player.login,
            'name': player.name,
            'email': player.email
        }))
    return (HttpResponse('Error: Password not correct!'))


# callback function used to get the info from the 42 API, if the user never conected before he is added to the database as a new user.
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

        if not PlayersModel.objects.filter(login=user_data['login']).exists():
            new_player = PlayersModel(
                login=user_data['login'],
                password='password',
                name=user_data['usual_full_name'],
                email=user_data['email'],
                secret_2fa = pyotp.random_base32()
            )
            new_player.save()

        return render(request, 'index.html', {
            'my42login': user_data['login'],
            'my42name': user_data['usual_full_name'],
            'my42email': user_data['email']
            })
 
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")
    
# used to connect with google but not very useful since i need to add manualy the mail that this code accept beforehand (but  it work)
@csrf_exempt
def google_auth(request):
    settings.GOOGLELOG = request.GET.get('login')
    settings.GOOGLENAME = request.GET.get('name')

    client_id = GOOGLE_OAUTH2_CLIENT_ID
    redirect_uri = 'https://127.0.0.1/google/callback'
    scopes = 'openid email profile'
    state = secrets.token_urlsafe(16)

    authorization_url = f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={state}'

    return JsonResponse({"authorization_url": authorization_url})

# callback handling from google API
@csrf_exempt
def google_callback(request):
    code = request.GET.get('code')

    try:
        token_response = requests.post('https://oauth2.googleapis.com/token', data={
            'code': code,
            'client_id': GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': GOOGLE_OAUTH2_CLIENT_SECRET,
            'redirect_uri': 'https://127.0.0.1/google/callback',
            'grant_type': 'authorization_code',
        })

        token_data = token_response.json()
        access_token = token_data['access_token']

        return render(request, 'index.html', {
            'my42login': settings.GOOGLELOG,
            'my42name': settings.GOOGLENAME
            })

    except Exception as e:
        return HttpResponse("Une erreur s'est produite lors de l'authentification.")

# verify the authenticator TOTP code
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
