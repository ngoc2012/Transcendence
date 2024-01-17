# myapp/urls.py
from django.urls import path
from .views import index, callback

urlpatterns = [
    path('', index, name='index'),
    path('callback/', callback, name='callback'),
]
