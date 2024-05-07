from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password
import secrets
import string

def generate_secure_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def create_user(username):
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        password = generate_secure_password()
        try:
            hashed_password = make_password(password)
            User.objects.create_user(username, '', hashed_password)
            # print(f"User created successfully.")
        except IntegrityError as e:
            pass
            # print(f"Failed to create user {username}: {e}")
        except Exception as e:
            pass
            # print(f"An error occurred while creating user {username}: {e}")

@receiver(post_migrate)
def signal_create_users(sender, **kwargs):
    create_user('localTournament1')
    create_user('localTournament2')
