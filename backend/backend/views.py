from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import PlayersModel

def index(request):
	return (render(request, 'index.html'))

def lobby(request):
	return (render(request, 'lobby.html'))

def signup(request):
	return (render(request, 'signup.html'))

@csrf_exempt
def new_player(request):
    if PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse({"error": "Login '" + request.POST['login'] + "' exist. Please login!"}))
    new_player = PlayersModel(
            login=request.POST['login'],
            password=request.POST['password'],
            name=request.POST['name'],
            x=0,
            y=0
            )
    new_player.save()
    return (HttpResponse({
        'login': new_player.login,
        'name': new_player.name
        }))

@csrf_exempt
def login(request):
    if PlayersModel.objects.filter(login=request.POST['login']).exists():
        return (HttpResponse({"error": "Login '" + request.POST['login'] + "' exist. Please login!"}))
    new_user = PlayersModel(
            login=request.POST['login'],
            password=request.POST['password'],
            name=request.POST['name'],
            x=0,
            y=0
            )
