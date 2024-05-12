# chat/urls.py
from django.urls import path, re_path

from . import views
from . import tournament

urlpatterns = [
    path("new", views.new_game, name="new_game"),
    path("join", views.join, name="join"),
    path("update", views.update, name="update"),
    path("ng", views.ng, name="ng"),
    path("jn", views.jn, name="jn"),
    path("need_update", views.need_update, name="need_update"),
    re_path(r'^close/(?P<login_id>.+)$', views.close_connection, name='close_connection'),
    path("tournament/local/join/", tournament.tournament_local_join, name="tournament_join"),
    path("tournament/local/join/setup/", tournament.tournament_local_join_setup, name="tournament_local_join_setup"),
    path('tournament/local/verify/', tournament.tournament_local_verify, name='tournament_local_verify'),
    path('tournament/local/get/', tournament.tournament_local_get, name='tournament_local_get'),
    path('tournament/local/result/', tournament.tournament_local_result, name='tournament_local_result'),
    path('tournament/local/adduser/', tournament.tournament_add_user, name='tournament_add_user'),
    path('tournament/local/2FAback', tournament.tournament_2FAback, name='tournament_2FAback'),
    path('tournament/local/delete', tournament.tournament_quit, name='tournament_quit'),
]
