"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from game.consumers import RoomsConsumer
from chat.consumers import ChatConsumer
from pong.consumers import PongConsumer

#from chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

#import chat.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter([
                re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
                re_path(r"ws/pong/(?P<room_id>\w+)/$", PongConsumer.as_asgi()),
                path("ws/game/rooms/", RoomsConsumer.as_asgi()),
            ]))
        ),
    }
)