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
    path("tournament/join", views.tournament_join, name="tournament_join")
]
