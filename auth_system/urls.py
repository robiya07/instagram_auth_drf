from django.urls import path
from auth_system.views import CustomUserRegistrationView

app_name = 'auth_system'

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
]
