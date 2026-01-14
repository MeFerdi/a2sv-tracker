"""
URL configuration for A2SVTracker project.
"""
from django.contrib import admin
from django.urls import path
from submission_app import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # Authentication
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Applicant routes
    path('applicant/', views.applicant_dashboard, name='applicant_dashboard'),
    path('applicant/submit/<int:question_id>/', views.submit_question, name='submit_question'),
    path('applicant/finalize/', views.finalize_application, name='finalize_application'),
    
    # Admin routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/questions/', views.question_management, name='question_management'),
    path('admin-dashboard/questions/create/', views.question_create, name='question_create'),
    path('admin-dashboard/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('admin-dashboard/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('admin-dashboard/applicants/', views.applicant_tracker, name='applicant_tracker'),
    path('admin-dashboard/applicants/export/', views.export_applicants, name='export_applicants'),
]
