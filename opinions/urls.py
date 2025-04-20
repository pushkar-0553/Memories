from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.user_login, name='login_page'),
    path('submit/', views.submit_opinion, name='submit_opinion'),
    path('search/', views.search_opinions, name='search_opinions'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('toggle-approval/<int:opinion_id>/', views.toggle_approval, name='toggle_approval'),
    path('toggle-author/<int:opinion_id>/', views.toggle_author, name='toggle_author'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Question management URLs
    path('add-question/', views.add_question, name='add_question'),
    path('toggle-question/<int:question_id>/', views.toggle_question, name='toggle_question'),
    path('get-questions/<int:student_id>/', views.get_questions, name='get_questions'),
    
    # Export and sharing URLs
    path('export/', views.export_memories, name='export_memories'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/cards/', views.print_cards, name='print_cards'),
    path('memory/<int:memory_id>/', views.view_memory, name='view_memory'),
    path('memories/<int:student_id>/', views.view_all_memories, name='view_all_memories'),
]
