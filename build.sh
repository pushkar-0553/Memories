#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')" | python manage.py shell

python manage.py import_students
