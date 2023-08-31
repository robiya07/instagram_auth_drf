from django.urls import path
from auth_system.views import CustomUserRegistrationView, ActivationUserGenericAPIView, UserTokenObtainPairView, \
    UserTokenRefreshView, UserTokenVerifyView, PasswordResetGenericAPIView, PasswordResetConfirmUpdateAPIView

app_name = 'auth_system'

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('register/activated-account/', ActivationUserGenericAPIView.as_view(), name='activated_account'),
    path('token/create/', UserTokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', UserTokenVerifyView.as_view(), name='token_verify'),
    path('reset-password/', PasswordResetGenericAPIView.as_view(), name='reset_password'),
    path('reset-password/confirm/', PasswordResetConfirmUpdateAPIView.as_view(), name='reset_password_confirm'),
]
