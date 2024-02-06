#!/bin/bash

cd /app/frontend/.

# Téléchargez qrcode.min.js depuis le CDN
wget -O qrcode.min.js https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js

# Assurez-vous que le dossier pour les fichiers JavaScript existe

# Incluez-le dans votre fichier HTML : Ajoutez une balise de script dans votre fichier HTML pour charger qrcode.min.js
# Ouvrez votre fichier HTML dans un éditeur et ajoutez la balise script, ou utilisez une commande sed pour le faire automatiquement
echo '<script src="qrcode.min.js"></script>' >> /app/frontend/display_2fa.html

chmod 755 /app/frontend/display_2fa.html


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

exec "$@"
