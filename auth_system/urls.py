from django.urls import path
from auth_system.views import CustomUserRegistrationView, ActivationUserGenericAPIView, UserTokenObtainPairView, \
    UserTokenRefreshView, UserTokenVerifyView

app_name = 'auth_system'

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('activated-account/', ActivationUserGenericAPIView.as_view(), name='activated_account'),
    path('token/create/', UserTokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', UserTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', UserTokenVerifyView.as_view(), name='token_verify'),
]
