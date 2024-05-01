from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import PlayersModelCreationForm, PlayersModelChangeForm
from .models import PlayersModel

class PlayersModelAdmin(UserAdmin):
    add_form = PlayersModelCreationForm
    form = PlayersModelChangeForm
    model = PlayersModel
    list_display = ["email", "username",]

admin.site.register(PlayersModel, PlayersModelAdmin, )