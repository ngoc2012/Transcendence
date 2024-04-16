# chat/urls.py
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("new", views.new_game, name="new_game"),
    path("join", views.join, name="join"),
    path("delete", views.delete, name="delete"),
    path("update", views.update, name="update"),
    path("need_update", views.need_update, name="need_update"),
    re_path(r'^close/(?P<login_id>.+)$', views.close_connection, name='close_connection'),
    path("tournament/local/join/", views.tournament_local_join, name="tournament_join"),
    path("tournament/local/join/setup/", views.tournament_local_join_setup, name="tournament_local_join_setup"),
    path('tournament/local/verify/', views.tournament_local_verify, name='tournament_local_verify'),
    path('tournament/local/get/', views.tournament_local_get, name='tournament_local_get'),
    path('tournament/local/result/', views.tournament_local_result, name='tournament_local_result'),
]
