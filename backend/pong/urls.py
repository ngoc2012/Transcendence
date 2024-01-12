from django.urls import path, re_path
from . import views
from .consumers import PongConsumer

app_name = 'pong'

urlpatterns = [
    path('', views.index, name='index'),
    re_path('room/(?P<room_name>\w+)/$', PongConsumer.as_asgi()),
]