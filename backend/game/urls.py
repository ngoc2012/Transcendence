# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("new", views.new_game, name="new_game"),
    path("join", views.join, name="join"),
    path("delete", views.delete, name="delete")
    # path("tournament/list/users", views.list_users, name="list_users")
]
