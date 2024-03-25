from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import PlayersModel

class PlayersModelCreationForm(UserCreationForm):

    class Meta:
        model = PlayersModel
        fields = ("username", "email")

class PlayersModelChangeForm(UserChangeForm):

    class Meta:
        model = PlayersModel
        fields = ("username", "email")
