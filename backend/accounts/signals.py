from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.db.utils import IntegrityError

@receiver(post_migrate)
def create_user(sender, **kwargs):
    User = get_user_model()

    if not User.objects.filter(username='localTournament1').exists():
        try:
            User.objects.create_user('localTournament1', '', 'lctrpswrd42')
            print("User created successfully.")
        except IntegrityError as e:
            print(f"Failed to create user: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    if not User.objects.filter(username='localTournament2').exists():
        try:
            User.objects.create_user('localTournament2', '', 'lctrpswrd42')
            print("User created successfully.")
        except IntegrityError as e:
            print(f"Failed to create user: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")