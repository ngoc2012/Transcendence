from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel

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
    if 'login' not in request.POST or 'password' not in request.POST or 'name' not in request.POST:
          return (HttpResponse({'Error: Form not correct!'}))
    if request.POST['login'] == "" or request.POST['password'] == "" or request.POST['name'] == "":
        return (HttpResponse({'Error : Form not correct!'}))
    if PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse({"Error: Login '" + request.POST['login'] + "' exist."}))
    new_player = PlayersModel(
            login=request.POST['login'],
            password=request.POST['password'],
            name=request.POST['name'],
            x=0,
            y=0
            )
    new_player.save()
    return (JsonResponse({
        'login': new_player.login,
        'name': new_player.name
        }))

@csrf_exempt
def log_in(request):
    if 'login' not in request.POST or 'password' not in request.POST:
        return (HttpResponse({'Error: Form not correct!'}))
    if not PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse({"Error: Login '" + request.POST['login'] + "' does not exist!"}))
    user = PlayersModel.objects.filter(login=request.POST['login'])
    if user.password == request.POST['password']:
        return (JsonResponse({
            'login': user.login,
            'name': user.name
        }))
    return (HttpResponse({'Error: Password not correct!'}))
