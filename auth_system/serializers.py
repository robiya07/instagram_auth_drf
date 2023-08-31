from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser
from auth_system.services.email import ActivationEmail
from auth_system.constants import Messages
from auth_system.services.cache_functions import getKey, deleteKey, setKey
import random
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework.settings import api_settings

User = get_user_model()
error_messages = Messages()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'phone_or_email', 'full_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self.context['user'] = user
        if not user.is_phone:
            ActivationEmail(self.context.get('request'), self.context).send([user.phone_or_email])
        else:
            activation_code = random.randint(100000, 999999)
            setKey(
                key=self.context.get('user').phone_or_email,
                value=activation_code,
                timeout=None
            )
            print(activation_code)
        return user


class CheckActivationSerializer(serializers.Serializer):
    activation_code = serializers.IntegerField(write_only=True)
    phone_or_email = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if getKey(attrs.get('phone_or_email')) != attrs.get('activation_code'):
            raise serializers.ValidationError({"invalid_code": error_messages.INVALID_ACTIVATE_CODE_ERROR})
        deleteKey(attrs.get('phone_or_email'))
        return attrs


class SendEmailResetSerializer(serializers.Serializer):
    phone_or_email = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = User.objects.get(phone_or_email=attrs.get('phone_or_email'))
        if not user:
            raise serializers.ValidationError({"user": error_messages.EMAIL_NOT_FOUND})
        self.context['user'] = user
        if not user.is_phone:
            ActivationEmail(self.context.get('request'), self.context).send([user.phone_or_email])
        else:
            activation_code = random.randint(100000, 999999)
            setKey(
                key=self.context.get('user').phone_or_email,
                value=activation_code,
                timeout=None
            )
            print(activation_code)
        return attrs


class PasswordResetConfirmSerializer(CheckActivationSerializer):
    new_password = serializers.CharField(max_length=150, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_or_email=attrs.get('phone_or_email'))
            validate_password(attrs.get('new_password'), user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return super().validate(attrs)
