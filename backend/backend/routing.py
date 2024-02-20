# chat/routing.py
from django.urls import path

# from .consumers import TournamentInviteConsumer
from .consumers import UserInviteConsumer

websocket_urlpatterns = [
        path('ws/user/invite/', UserInviteConsumer.as_asgi()),
        # path('ws/tournament/invite/<uuid:tournament_id>/', TournamentInviteConsumer.as_asgi()),
]