"""
URL configuration for A2SVTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from submission_app.views import (
    InviteRegisterView,
    LoginView,
    ProfileView,
    ApplicantQuestionListView,
    FinalizeApplicationView,
    QuestionAdminViewSet,
    ApplicantTrackerView,
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'admin/questions', QuestionAdminViewSet, basename='question')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Token endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authentication endpoints
    path('api/auth/register/', InviteRegisterView.as_view(), name='invite_register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    
    # Applicant endpoints
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/questions/', ApplicantQuestionListView.as_view(), name='applicant_questions'),
    path('api/finalize/', FinalizeApplicationView.as_view(), name='finalize_application'),
    
    # Admin endpoints
    path('api/admin/applicants/', ApplicantTrackerView.as_view(), name='applicant_tracker'),
    
    # Include router URLs for ViewSets
    path('api/', include(router.urls)),
]
