#!/bin/bash

cd /app/frontend/.
mkdir media
cd /app/backend/.
python3 manage.py makemigrations
python3 manage.py migrate

# Attempt to create a superuser
# if python3 manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null; then
if python3 manage.py createsuperuser --noinput --login "$DJANGO_SUPERUSER_USERNAME" --username "$DJANGO_SUPERUSER_USERNAME" 2>/dev/null; then
    # If successful, change the password using changesuperuserpw.py
    # python3 manage.py changesuperuserpw.py -n "$DJANGO_SUPERUSER_USERNAME" -p "$DJANGO_SUPERUSER_PASSWORD"
    echo "from accounts.models import PlayersModel; user = PlayersModel.objects.get(login='$DJANGO_SUPERUSER_USERNAME'); user.set_password('$DJANGO_SUPERUSER_PASSWORD'); user.save()" | python3 manage.py shell
    echo "Superuser created successfully."
else
    # Handle the case where createsuperuser fails
    exit_code=$?
    if [ $exit_code -eq 1 ]; then
        echo "Username '$DJANGO_SUPERUSER_USERNAME' is already taken. Exiting."
    else
        # Handle other errors if needed
        echo "An error occurred while creating the superuser. Exit code: $exit_code. Exiting."
    fi
fi

exec "$@"
