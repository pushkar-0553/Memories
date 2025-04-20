# Class Memories - Anonymous Opinion Sharing App

A Django web application for B.Tech students to share anonymous opinions about their classmates.

## Features

- Anonymous opinion submission
- Personal opinion search
- Admin panel for moderation
- Mobile-friendly UI
- Secure authentication

## Local Development Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run development server:
   ```bash
   python manage.py runserver
   ```

## Deployment

1. Create an account on PythonAnywhere
2. Upload the project files
3. Set up a virtual environment and install dependencies
4. Configure WSGI file
5. Set environment variables
6. Update allowed hosts
7. Collect static files

## Security Notes

- Admin access is password-protected
- Input sanitization implemented
- Author tracking for moderation
- Rate limiting on submissions
