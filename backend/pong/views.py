from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from game.models import RoomsModel, PlayersModel, PlayerRoomModel
from asgiref.sync import sync_to_async

from pong.data import pong_data
from channels.layers import get_channel_layer

# Create your views here.
def index(request):
    return render(request, "pong.html")
