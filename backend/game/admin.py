from django.contrib import admin

# Register your models here.
from .models import PlayersModel, RoomsModel, PlayerRoomModel, TournamentMatchModel, TournamentModel

admin.site.register(PlayersModel)
admin.site.register(RoomsModel)
admin.site.register(PlayerRoomModel)
admin.site.register(TournamentModel)
admin.site.register(TournamentMatchModel)