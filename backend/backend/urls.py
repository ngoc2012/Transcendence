from django.urls import include, path, re_path
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import callback, csrf

urlpatterns = [
    path('', views.index, name='index'),
    path('get-csrf/', csrf, name='get-csrf'),
    path("game/", include("game.urls")),
    path('admin/', admin.site.urls),
    path('lobby/', views.lobby, name='lobby'),
    path('pages/signup/', views.signup, name='signup'),
    path('pages/login/', views.login, name='login'),
    path('log_in/', views.log_in, name='log_in'),
    path('lg/', views.lg, name='lg'),
    path('auth_view/', views.auth_view, name='auth_view'),
    path('logout/', views.logout, name='logout'),
    path('new_player/', views.new_player, name='new_player'),
    path('np/', views.np, name='np'),
    path('pong/', include("pong.urls", namespace='pong')),
    path('callback/', callback, name='callback'),
    path('transchat/', include("transchat.urls")),
    path('twofa/', views.twofa, name='twofa'),
    path('display_2fa/', views.display_2fa, name='display_2fa'),
    path('qrcode_2fa/', views.qrcode_2fa, name='qrcode_2fa'),
    path('mail_2fa/', views.mail_2fa, name='mail_2fa'),
    path('code_2fa/', views.code_2fa, name='code_2fa'),
    path('verify/', views.verify, name='verify'),
    path('verify_qrcode/', views.verify_qrcode, name='verify_qrcode'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/alias/', views.alias, name='alias'),
    path('profile/<str:username>/change_password/', views.password, name='password'),
    path('profile/<str:username>/change_email/', views.email, name="email"),
    path('profile/<str:username>/change_login/', views.change_login, name="change_login"),
    path('profile/<str:username>/change_name/', views.name, name="name"),
    path('profile/<str:username>/add_friend/', views.friend, name="friend"),
    path('profile/<str:username>/change_avatar/', views.avatar, name="avatar"),
    path('tournament/request/', views.tournament_request, name="tournament_request"),
    path('tournament/', views.tournament, name='tournament'),
    path('tournament_history/', views.tournament_history, name='tournament_history'),
    path('get_tournament_data/', views.get_tournament_data, name='get_tournament_data'),
    path('tournament/new/', views.new_tournament, name='new_tournament'),
    path('tournament/local/', views.tournament_local, name='tournament_local'),
    path('tournament/local/start/', views.tournament_local_start, name='tournament_local_start'),
    path('validate-session/', views.validate_session, name='validate_session'),
    path('login42/', views.login42, name='login42'),
    re_path(r'^.*$', views.redirect, name='redirect'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
