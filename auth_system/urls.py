from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from auth_system.views import (UserRegistrationView, UserTokenObtainPairView,
                               VerifyGenericAPIView, PasswordResetConfirmUpdateAPIView, PasswordResetGenericAPIView,
                               PasswordChangeGenericAPIView)

app_name = 'auth_system'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register/verify/', VerifyGenericAPIView.as_view(), name='verify'),

    path('login/', UserTokenObtainPairView.as_view(), name='login'),
    path('login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('password_reset/', PasswordResetGenericAPIView.as_view(), name='password_reset'),
    path('password_reset/confirm/', PasswordResetConfirmUpdateAPIView.as_view(), name='password_reset_confirm'),
    path('password_change/', PasswordChangeGenericAPIView.as_view(), name='password_change'),
]
