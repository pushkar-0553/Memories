from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='vema').exists():
            User.objects.create_superuser(
                username='vema',
                email='vemalathay@gmail.com',
                password='Vema@123'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
