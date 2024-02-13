from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel, TournamentModel
import requests
import os

API_PUBLIC = os.environ.get('API_PUBLIC')
API_SECRET = os.environ.get('API_SECRET')

def index(request):
	return (render(request, 'index.html'))

def lobby(request):
	return (render(request, 'lobby.html'))

def signup(request):
	return (render(request, 'signup.html'))

def login(request):
	return (render(request, 'login.html'))

def tournament(request):
     return (render(request, 'tournament.html'))

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
        print('User Information:', user_data['login'])
        print('User Information:', user_data['usual_full_name'])

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
    
@csrf_exempt
def new_tournament(request):
    if request.method == 'POST':
        # print("ok")
        name = request.POST.get('name')
        game = request.POST.get('game')
        owner = PlayersModel.objects.get(login=request.POST['login'])
        try:
            # print("ok")
            tournament = TournamentModel(name=name, game=game, owner=owner)
            return JsonResponse({'success': 'Tournament created successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
         return JsonResponse({'error': 'Invalid request'}, status=405)

    
        
