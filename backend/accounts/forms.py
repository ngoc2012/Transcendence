from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import PlayersModel
from django import forms

class PlayersModelCreationForm(UserCreationForm):

    class Meta:
        model = PlayersModel
        fields = ("username", "email")

class PlayersModelChangeForm(UserChangeForm):

    class Meta:
        model = PlayersModel
        fields = ("username", "email")


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Choose a new profile picture")
