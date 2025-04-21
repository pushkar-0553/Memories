from django.core.management.base import BaseCommand
import csv
from opinions.models import Student
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Import students from CSV'

    def handle(self, *args, **options):
        try:
            with open('initial_students.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create or update user
                    user, created = User.objects.get_or_create(
                        username=row['username'],
                        defaults={
                            'email': row['email'],
                            'first_name': row['first_name'],
                            'last_name': row['last_name']
                        }
                    )
                    
                    if not created:
                        user.email = row['email']
                        user.first_name = row['first_name']
                        user.last_name = row['last_name']
                        user.save()
                    
                    # Set a default password for the user
                    if created:
                        user.set_password(row['username'])  # Using username as initial password
                        user.save()
                    
                    # Create or update student
                    student, _ = Student.objects.get_or_create(
                        user=user,
                        defaults={'roll_number': row['roll_number']}
                    )
                    if student.roll_number != row['roll_number']:
                        student.roll_number = row['roll_number']
                        student.save()
                    
            self.stdout.write(self.style.SUCCESS('Successfully imported students'))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING('No initial_students.csv file found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing students: {str(e)}'))
