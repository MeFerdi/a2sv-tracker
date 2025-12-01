from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import InviteRegisterView, ProfileView

app_name = 'submission_app'

urlpatterns = [
    path('auth/invite/register/', InviteRegisterView.as_view(), name='invite_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('user/profile/', ProfileView.as_view(), name='profile'),
]

