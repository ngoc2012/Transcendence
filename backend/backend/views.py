from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel
import requests
import os

API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
GOOGLE_OAUTH2_PROJECT_ID = os.environ.get('GOOGLE_OAUTH2_PROJECT_ID')

def index(request):
	return (render(request, 'index.html'))

def lobby(request):
	return (render(request, 'lobby.html'))

def signup(request):
	return (render(request, 'signup.html'))

def login(request):
	return (render(request, 'login.html'))

@csrf_exempt
def new_player(request):
    if 'login' not in request.POST or request.POST['login'] == "":
        return (HttpResponse("Error: No login!"))
    if 'password' not in request.POST or request.POST['password'] == "":
        return (HttpResponse("Error: No password!"))
    if 'name' not in request.POST or request.POST['name'] == "":
        return (HttpResponse("Error: No name!"))
    if PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse("Error: Login '" + request.POST['login'] + "' exist."))
    new_player = PlayersModel(
        login=request.POST['login'],
        password=request.POST['password'],
        name=request.POST['name']
    )
    new_player.save()
    return (JsonResponse({
        'login': new_player.login,
        'name': new_player.name
        }))

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
            'name': player.name
        }))
    return (HttpResponse('Error: Password not correct!'))

@csrf_exempt
def callback(request):
    code = request.GET.get('code')

    print('DATA:', API_PUBLIC)

    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': API_PUBLIC,
            'client_secret': API_SECRET,
            'code': code,
            'redirect_uri': 'https://127.0.0.1/callback/',
        })

        token_data = token_response.json()
        access_token = token_data['access_token']
        
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })


        user_data = user_response.json()
        # print('User Information:', user_data['login'])
        # print('User Information:', user_data['usual_full_name'])

        if not PlayersModel.objects.filter(login=user_data['login']).exists():
            new_player = PlayersModel(
                login=user_data['login'],
                password='password',
                name=user_data['login']
            )
            new_player.save()

        return render(request, 'index.html', {
            'my42login': user_data['login'],
            'my42name': user_data['usual_full_name']
            })
 
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")
    

def twofa(request):
    	return (render(request, 'twofa.html'))

# demander l'email a la connection -> lié l'email au pseudo
# recup l'email dans la db et le pseudo associé

#voir avec les sessions

@csrf_exempt
def googleauth(request):
    code = request.GET.get('code')
    # my42login = request.GET.get('my42login', '')
    # my42name = request.GET.get('my42name', '') 

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

        user_response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
            'Authorization': f'Bearer {access_token}',
        })

        return render(request, 'index.html', {
            'my42login': 'tt',
            'my42name': 'tt'
            })


    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred.")