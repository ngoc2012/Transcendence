from django.contrib import admin

# Register your models here.
from .models import RoomsModel, PlayerRoomModel, TournamentMatchModel, TournamentModel
from accounts.models import PlayersModel

# admin.site.register(PlayersModel)
admin.site.register(RoomsModel)
admin.site.register(PlayerRoomModel)
admin.site.register(TournamentModel)
admin.site.register(TournamentMatchModel)