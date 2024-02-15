"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.urls import include, path
from .views import callback

urlpatterns = [
    path('', views.index, name='index'),
    path("chat/", include("chat.urls")),
    path("game/", include("game.urls")),
    path('admin/', admin.site.urls),
    path('lobby/', views.lobby, name='lobby'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('log_in/', views.log_in, name='log_in'),
    path('new_player/', views.new_player, name='new_player'),
    path('pong/', include("pong.urls", namespace='pong')),
    path('callback/', callback, name='callback'),
    path('tournament/', views.tournament, name='tournament'),
    path('tournament/new/', views.new_tournament, name='new_tournament'),
    path('tournament/lobby/', views.tournament_lobby, name='tournament_lobby'),
    path("tournament/list/users/", views.list_users, name="list_users")
]
