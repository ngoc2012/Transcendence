#!/bin/bash

cd /app/backend/.
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
python3 changesuperuserpw.py -n "$DJANGO_SUPERUSER_USERNAME" -p "$DJANGO_SUPERUSER_PASSWORD"

echo "Superuser created successfully."

exec "$@"