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

class PlayerChangeNameForm(forms.Form):
    login = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

class PlayerChangeLoginForm(forms.Form):
    login = forms.CharField(max_length=255)
    new_login = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

class PlayerChangeEmailForm(forms.Form):
    login = forms.CharField(max_length=255)
    email = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())

class PlayerChangeAliasForm(forms.Form):
    alias = forms.CharField(max_length=255)

class PlayerChangePasswordForm(forms.Form):
    oldpwd = forms.CharField(widget=forms.PasswordInput())
    newpwd = forms.CharField(widget=forms.PasswordInput())

class PlayerAddFriendForm(forms.Form):
    type = forms.CharField(max_length=255)
    friend = forms.CharField(max_length=255)
    sender = forms.CharField(max_length=255)
    response = forms.CharField(required=False)

class ChatMessageForm(forms.Form):
    type = forms.CharField(max_length=255)
    user = forms.CharField(max_length=255)
    message = forms.CharField(max_length=255)
    
    def __init__(self, type, user, message):
        self.type = type
        self.user = user
        self.message = message

class UploadFileForm(forms.Form):
    id_file = forms.FileField(label="")

    # def __init__(self, id_file):
    #     self.id_file = id_file
