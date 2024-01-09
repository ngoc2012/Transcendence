from django.shortcuts import render
#from django.http import HttpResponse
#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from django.shortcuts import redirect
#import time
#from random import randrange

# Create your views here.
def index(request):
    return render(request, "pong.html")

#def room(request, room_name):
#    return render(request, "chat/room.html", {"room_name": room_name})
