#!/bin/bash

cd /app/backend/.
python3 manage.py migrate


# solution 1 : 
# python3 manage.py createsuperuser --noinput --username "admin" --email "admin@gmail.com"
# python3 changesuperuserpw.py -n "admin" -p "admin"

#solution 2 : 
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')" | python3 manage.py shell


python3 manage.py runserver 0.0.0.0:8000
