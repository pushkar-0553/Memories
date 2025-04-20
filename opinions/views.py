from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from .models import Opinion, Student, Question, Answer
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from datetime import datetime

@login_required
def submit_opinion(request):
    # Exclude current user from the list of students
    students = Student.objects.exclude(user=request.user)
    selected_student = None
    questions = []

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        content = request.POST.get('content')
        if recipient_id and content:
            try:
                recipient = Student.objects.get(id=recipient_id)
                opinion = Opinion.objects.create(
                    recipient=recipient,
                    content=content,
                    author=request.user if request.user.is_authenticated else None
                )
                
                # Handle question answers
                for key, value in request.POST.items():
                    if key.startswith('answer_') and value.strip():
                        question_id = int(key.split('_')[1])
                        try:
                            question = Question.objects.get(id=question_id, student=recipient)
                            Answer.objects.create(
                                question=question,
                                opinion=opinion,
                                answer_text=value.strip()
                            )
                        except Question.DoesNotExist:
                            pass
                
                messages.success(request, 'Memory submitted successfully!')
                return redirect('submit_opinion')
            except Student.DoesNotExist:
                messages.error(request, 'Invalid student selected.')
    else:
        # Get questions for selected student
        student_id = request.GET.get('student')
        if student_id:
            try:
                selected_student = Student.objects.get(id=student_id)
                questions = Question.objects.filter(student=selected_student, is_active=True)
            except Student.DoesNotExist:
                messages.error(request, 'Student not found.')

    return render(request, 'opinions/submit.html', {
        'students': students,
        'selected_student': selected_student,
        'questions': questions
    })

@login_required
def search_opinions(request):
    try:
        student = Student.objects.get(user=request.user)
        # Get all opinions for the current student
        opinions_query = Opinion.objects.filter(recipient=student)
        
        # If user is staff, show all opinions regardless of approval status
        if request.user.is_staff:
            opinions = opinions_query.order_by('-created_at')
        else:
            # For regular users, only show approved opinions
            opinions = opinions_query.filter(is_approved=True).order_by('-created_at')
                
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        opinions = []
    
    return render(request, 'opinions/search.html', {
        'opinions': opinions,
        'is_admin': request.user.is_staff
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    opinions = Opinion.objects.all()
    return render(request, 'opinions/admin.html', {'opinions': opinions})

@login_required
def toggle_approval(request, opinion_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    opinion = get_object_or_404(Opinion, id=opinion_id)
    opinion.is_approved = not opinion.is_approved
    opinion.save()
    return JsonResponse({'status': 'success', 'is_approved': opinion.is_approved})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin:index')
            # Check if this is their first login (using default password)
            if user.check_password(username):  # Default password is same as username
                messages.warning(request, 'Please change your password.')
                return redirect('change_password')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'opinions/login_new.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')
    questions = Question.objects.filter(student=student)
    opinions = Opinion.objects.filter(recipient=student).select_related('author', 'author__student')
    
    # Process opinions to show author only if allowed
    processed_opinions = []
    for opinion in opinions:
        opinion_data = {
            'content': opinion.content,
            'created_at': opinion.created_at,
            'author_name': None
        }
        if opinion.show_author and opinion.author:
            opinion_data['author_name'] = opinion.author.student.name
        processed_opinions.append(opinion_data)
    
    return render(request, 'opinions/profile.html', {
        'student': student,
        'questions': questions,
        'opinions': processed_opinions
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'opinions/change_password.html', {'form': form})

@login_required
def add_question(request):
    if request.method == 'POST':
        text = request.POST.get('question_text')
        if text:
            student = get_object_or_404(Student, user=request.user)
            Question.objects.create(student=student, text=text)
            messages.success(request, 'Question added successfully!')
        else:
            messages.error(request, 'Question text is required.')
    return redirect('profile')

@login_required
def toggle_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.student.user == request.user:
        question.is_active = not question.is_active
        question.save()
    return redirect('profile')

@login_required
def get_questions(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        questions = Question.objects.filter(student=student, is_active=True)
        return JsonResponse({
            'questions': [{
                'id': q.id,
                'text': q.text
            } for q in questions]
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

@login_required
def toggle_author(request, opinion_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    opinion = get_object_or_404(Opinion, id=opinion_id)
    opinion.show_author = not opinion.show_author
    opinion.save()
    messages.success(request, f'Author visibility has been {"shown" if opinion.show_author else "hidden"}')
    return redirect('admin_dashboard')

@login_required
def export_memories(request):
    try:
        student = Student.objects.get(user=request.user)
        opinions = Opinion.objects.filter(recipient=student, is_approved=True).order_by('-created_at')
        share_url = request.build_absolute_uri(f'/memories/{student.id}/')
        
        return render(request, 'opinions/export_memories.html', {
            'opinions': opinions,
            'share_url': share_url
        })
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('profile')

@login_required
def export_pdf(request):
    try:
        student = Student.objects.get(user=request.user)
        opinions = Opinion.objects.filter(recipient=student, is_approved=True).order_by('-created_at')
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            spaceAfter=20,
            alignment=1
        )
        memory_style = ParagraphStyle(
            'MemoryStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            leading=16
        )
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.blue,
            leftIndent=20
        )
        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=40
        )
        
        # Create the story (content)
        story = []
        
        # Add title
        story.append(Paragraph(f"{student.name}'s College Memories", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style))
        story.append(Spacer(1, 20))
        
        # Add memories
        for opinion in opinions:
            # Memory content
            story.append(Paragraph(
                f"<i>{opinion.created_at.strftime('%B %d, %Y')}</i><br/><br/>{opinion.content}",
                memory_style
            ))
            
            # Add questions and answers
            answers = Answer.objects.filter(opinion=opinion)
            if answers.exists():
                for answer in answers:
                    story.append(Paragraph(f"Q: {answer.question.text}", question_style))
                    story.append(Paragraph(f"A: {answer.answer_text}", answer_style))
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        # Get the value of the BytesIO buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        filename = f'memories_{slugify(student.name)}_{datetime.now().strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('profile')

@login_required
def print_cards(request):
    try:
        student = Student.objects.get(user=request.user)
        opinions = Opinion.objects.filter(recipient=student, is_approved=True).order_by('-created_at')
        
        # Create PDF buffer
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Card dimensions
        card_width = width / 2 - 40
        card_height = height / 3 - 40
        margin = 20
        
        # Generate cards
        x, y = margin, height - margin - card_height
        for i, opinion in enumerate(opinions):
            if i > 0 and i % 6 == 0:  # New page after every 6 cards
                p.showPage()
                x, y = margin, height - margin - card_height
            
            # Draw card background
            p.setFillColor(colors.white)
            p.roundRect(x, y, card_width, card_height, 10, fill=1)
            
            # Draw content
            p.setFillColor(colors.black)
            p.setFont('Helvetica-Bold', 12)
            date_text = opinion.created_at.strftime('%B %d, %Y')
            p.drawString(x + 10, y + card_height - 20, date_text)
            
            # Draw memory text with word wrap
            p.setFont('Helvetica', 10)
            text = opinion.content
            words = text.split()
            lines = []
            current_line = []
            for word in words:
                if p.stringWidth(' '.join(current_line + [word])) < card_width - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            for j, line in enumerate(lines[:4]):  # Limit to 4 lines
                p.drawString(x + 10, y + card_height - 40 - (j * 15), line)
            
            # Update position for next card
            if x + card_width + margin * 2 <= width:
                x += card_width + margin
            else:
                x = margin
                y -= card_height + margin
        
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='memory_cards.pdf')
    
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('profile')

@login_required
def view_memory(request, memory_id):
    memory = get_object_or_404(Opinion, id=memory_id)
    if not memory.is_approved:
        messages.error(request, 'This memory is not available.')
        return redirect('profile')
    
    return render(request, 'opinions/view_memory.html', {
        'memory': memory
    })

@login_required
def view_all_memories(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    opinions = Opinion.objects.filter(recipient=student, is_approved=True).order_by('-created_at')
    
    return render(request, 'opinions/view_all_memories.html', {
        'student': student,
        'opinions': opinions
    })
