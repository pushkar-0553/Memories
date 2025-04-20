from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from io import TextIOWrapper
from .models import Student, Opinion, Question, Answer

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'total_opinions_received', 'total_questions')
    search_fields = ('name', 'roll_number')
    ordering = ('roll_number',)
    change_list_template = 'admin/student/change_list.html'
    fields = ('name', 'roll_number')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['roll_number'].help_text = 'This will be used as initial username and password'
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new students
            # Create user with roll number as username and password
            user = User.objects.create_user(
                username=obj.roll_number,
                password=obj.roll_number  # Initial password is roll number
            )
            obj.user = user
        super().save_model(request, obj, form, change)
    
    def total_opinions_received(self, obj):
        count = Opinion.objects.filter(recipient=obj).count()
        return format_html('<b>{}</b>', count)
    
    def total_questions(self, obj):
        count = Question.objects.filter(student=obj).count()
        return count

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv, name='upload-csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if csv_file:
                try:
                    decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                    reader = csv.DictReader(decoded_file)
                    count = 0
                    for row in reader:
                        roll_number = row.get('roll_number')
                        name = row.get('name')
                        if roll_number and name:
                            if not Student.objects.filter(roll_number=roll_number).exists():
                                # Create user with roll number as both username and password
                                user = User.objects.create_user(
                                    username=roll_number,
                                    password=roll_number
                                )
                                Student.objects.create(
                                    user=user,
                                    name=name,
                                    roll_number=roll_number
                                )
                                count += 1
                    messages.success(request, f'Successfully added {count} students')
                except Exception as e:
                    messages.error(request, f'Error uploading CSV: {str(e)}')
            else:
                messages.error(request, 'Please select a CSV file')
            return redirect('..')
        return render(request, 'admin/csv_upload.html')

@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'content_preview', 'author_name', 'created_at', 'show_author')
    list_filter = ('show_author', 'created_at')
    search_fields = ('content', 'recipient__name', 'author__username')
    actions = ['show_authors', 'hide_authors']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    def author_name(self, obj):
        if obj.author:
            return obj.author.student.name
        return 'Anonymous'

    def show_authors(self, request, queryset):
        queryset.update(show_author=True)
    show_authors.short_description = 'Show authors for selected opinions'

    def hide_authors(self, request, queryset):
        queryset.update(show_author=False)
    hide_authors.short_description = 'Hide authors for selected opinions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('student', 'text', 'is_active', 'answer_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text', 'student__name')

    def answer_count(self, obj):
        return obj.answers.count()
