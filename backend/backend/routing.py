# chat/routing.py
from django.urls import path

from .consumers import TournamentInviteConsumer

websocket_urlpatterns = [
        path('ws/tournament/invite/<uuid:tournament_id>/', TournamentInviteConsumer.as_asgi()),
]