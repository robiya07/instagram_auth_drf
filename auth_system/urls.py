from django.urls import path
from auth_system.views import CustomUserRegistrationView, ActivationUserGenericAPIView

app_name = 'auth_system'

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('activated-account/', ActivationUserGenericAPIView.as_view(), name='activated_account'),
]
