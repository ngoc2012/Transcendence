from django.urls import path, re_path
from . import views

app_name = 'pong'

urlpatterns = [
    path('', views.index, name='index'),
    #path('state', views.state, name='state')
]
