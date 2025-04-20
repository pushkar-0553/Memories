from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from opinions.models import Student

class Command(BaseCommand):
    help = 'Create initial student accounts with roll numbers'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='CSV file with student data (roll_number,name)')

    def handle(self, *args, **options):
        # Example students (you can replace this with file reading logic)
        students = [
            ('21001', 'Student One'),
            ('21002', 'Student Two'),
            ('21003', 'Student Three'),
            # Add more students as needed
        ]

        for roll_number, name in students:
            # Create user with roll number as both username and password
            if not User.objects.filter(username=roll_number).exists():
                user = User.objects.create_user(
                    username=roll_number,
                    password=roll_number  # Initial password is same as roll number
                )
                
                # Create student profile
                Student.objects.create(
                    user=user,
                    name=name,
                    roll_number=roll_number
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created student account for {name} ({roll_number})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Student with roll number {roll_number} already exists')
                )
