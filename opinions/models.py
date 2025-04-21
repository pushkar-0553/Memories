from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

@receiver([post_save, post_delete], sender=Student)
def backup_students(sender, instance, **kwargs):
    """Automatically export students data when a student is added, modified, or deleted"""
    try:
        call_command('export_students')
    except Exception as e:
        print(f'Error during backup: {str(e)}')

    class Meta:
        ordering = ['name']

class Question(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Question by {self.student.name}: {self.text[:50]}...'

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    opinion = models.ForeignKey('Opinion', on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Answer to {self.question.text[:30]}...'

class Opinion(models.Model):
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_opinions')
    content = models.TextField()
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    show_author = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Opinion about {self.recipient}'
