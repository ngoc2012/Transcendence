"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from . import views
#from .api.urls import 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/pong', include('api.pong.urls')),
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('pong/', views.pong, name='pong'),
    path('pong_state/', views.pong_state, name='pong_state'),
    path('new_player/', views.new_player, name='new_player'),
    path('start_game/', views.start_game, name='start_game'),
    path('online_players_list/', views.online_players_list, name='online_players_list'),
    path('invite/', views.invite, name='invite'),
    path('accept_invitation/', views.accept_invitation, name='accept_invitation'),
    path('cancel_invitation/', views.cancel_invitation, name='cancel_invitation'),
    path('check_game_status/', views.check_game_status, name='check_game_status'),
]
