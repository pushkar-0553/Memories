#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser
echo "from django.contrib.auth.models import User; User.objects.create_superuser('vema', 'vemalathay@gmail.com', 'Vema@123') if not User.objects.filter(username='vema').exists() else print('Superuser already exists')" | python manage.py shell

python manage.py import_students
