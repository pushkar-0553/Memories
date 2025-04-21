from django.core.management.base import BaseCommand
import csv
from opinions.models import Student
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Export students data to CSV'

    def handle(self, *args, **options):
        with open('initial_students.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'email', 'first_name', 'last_name', 'roll_number'])
            
            students = Student.objects.all()
            for student in students:
                user = student.user
                writer.writerow([
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    student.roll_number
                ])
            
            self.stdout.write(self.style.SUCCESS(f'Successfully exported {students.count()} students'))
