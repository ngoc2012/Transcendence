from django.urls import path, re_path
from . import views

app_name = 'pong'

urlpatterns = [
    re_path(r'(?P<room_id>[0-9a-f-]+)/(?P<player_id>[0-9a-f-]+)/(?P<action>[a-z]+)$', views.action, name='action'),
    re_path(r'start/(?P<room_id>[0-9a-f-]+)$', views.start, name='start'),
    re_path(r'close/(?P<room_id>[0-9a-f-]+)/(?P<player_id>[0-9a-f-]+)$', views.close_connection, name='close_connection'),
    path('load_font', views.load_font, name='load_font'),
    path('', views.index, name='index'),
]
