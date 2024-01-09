"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from pong.consumers import PongConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

#application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r"ws/pong/(?P<room_name>\w+)/$", PongConsumer.as_asgi()),
            ]
        )
    ),
})
