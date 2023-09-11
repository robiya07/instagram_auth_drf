from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from rest_framework_simplejwt.tokens import RefreshToken

from auth_system.models import NEW, CODE_VERIFIED, User, UserConfirmation
from auth_system.serializers import RegisterUserSerializer, UserLoginSerializer, PasswordResetConfirmSerializer, \
    SendEmailResetSerializer, PasswordChangeSerializer, VerifyCodeSerializer
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from auth_system.services import email


class UserRegistrationView(CreateAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data, is_active=False)
        if user.email:
            code = user.create_verify_code(user.auth_type)
            email.EmailActivation(self.request, serializer.context, activation_code=code).send([user.email])
        else:
            code = user.create_verify_code(user.auth_type)
            email.phone_activation(user.phone_number, code)

        s_data = serializer.validated_data
        data = {
            'status': '201',
            'message': 'Registration completed successfully.',
            'data': [
                {
                    'email_phone': s_data.get('email') or s_data.get('phone_number'),
                    'full_name': s_data.get('first_name') + ' ' + s_data.get('last_name'),
                    'username': s_data.get('username'),
                    'password': s_data.get('password')
                }
            ]
        }
        return Response(data, status=status.HTTP_201_CREATED)


class VerifyGenericAPIView(GenericAPIView):
    serializer_class = VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        user = serializer.validated_data.get('user')
        self.check_verify(user, code)
        data = {
            'status': '200',
            'message': 'Verification successful.',
            'data': [
                {
                    'email_phone': user.email or user.phone_number,
                    'activation_code': code
                }
            ]
        }
        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.is_active = True
            user.save()
        return True


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = serializer.context.get('user')
            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token

            data = {
                'status': '200',
                'message': 'Login successful.',
                'data': [
                    {
                        'access_token': str(access_token),
                        "refresh_token": str(refresh_token)
                    }
                ]
            }
            return Response(data, status=status.HTTP_200_OK)
        return response


class PasswordResetGenericAPIView(GenericAPIView):
    serializer_class = SendEmailResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'status': '200',
            'message': 'Code sent successfully.',
            'data': [
                {
                    'email_phone': serializer.validated_data.get('email_phone')
                }
            ]
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetConfirmUpdateAPIView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get('new_password')
        user = serializer.context.get('user')
        user.password = make_password(password)
        user.save(update_fields=["password"])
        data = {
            'status': '200',
            'message': 'Password reset successfully.',
            'data': [
                {
                    'email_phone': user.email or user.phone_number,
                    'password': password
                }
            ]
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordChangeGenericAPIView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get('new_password')
        user = self.request.user
        print('user', user)
        user.password = make_password(password)
        user.save()
        data = {
            'status': '200',
            'message': 'Password change successfully.',
            'data': [
                {
                    'username': user.username,
                    'old_password': serializer.validated_data.get('old_password'),
                    'new_password': password
                }
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
