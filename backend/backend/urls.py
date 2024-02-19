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
    path('twofa/', views.twofa, name='twofa'),
    path('display_2fa/', views.display_2fa, name='display_2fa'),
    path('qrcode_2fa/', views.qrcode_2fa, name='qrcode_2fa'),
    path('mail_2fa/', views.mail_2fa, name='mail_2fa'),
    path('code_2fa/', views.code_2fa, name='code_2fa'),
    path('verify/', views.verify, name='verify'),
    path('verify_qrcode/', views.verify_qrcode, name='verify_qrcode'),

]   



