#!/bin/bash


cd /app/backend/.
python3 manage.py makemigrations
python3 manage.py migrate

# Attempt to create a superuser
if python3 manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null; then
    # If successful, change the password using changesuperuserpw.py
    python3 changesuperuserpw.py -n "$DJANGO_SUPERUSER_USERNAME" -p "$DJANGO_SUPERUSER_PASSWORD"
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


#deploy smart contracts

cd /app/blockchain/.

contract_json="build/contracts/TournamentRegistry.json"

if [ ! -f "$contract_json" ]; then
    echo "Deploying smart contracts..."
    truffle deploy
else
    echo "Contracts already deployed. Skipping deployment."
fi


cd /app/backend/.

exec "$@"
