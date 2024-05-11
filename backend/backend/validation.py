from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
import uuid

class NewPlayerForm(forms.Form):
    login = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=150, required=False)

    def clean_login(self):
        login = self.cleaned_data['login']
        User = get_user_model()
        if User.objects.filter(username=login).exists():
            raise forms.ValidationError("This login is already taken.")
        return login

    def clean_email(self):
        email = self.cleaned_data['email']
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        password_validation.validate_password(password)
        return password

class AddTournamentUserForm(forms.Form):
    login = forms.CharField(required=False)
    password = forms.CharField(required=False)
    userLogin = forms.ChoiceField(choices=(('true', 'True'), ('false', 'False')))

class TournamentNameForm(forms.Form):
    name = forms.CharField(required=True)

class verifyQrCodeForm(forms.Form):
    input_code = forms.IntegerField(required=True)

class verifyLoginForm(forms.Form):
    login = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class verifyCodeForm(forms.Form):
    input_code = forms.IntegerField(required=True)

