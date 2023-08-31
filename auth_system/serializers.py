from django.contrib.auth import get_user_model, password_validation
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser
from auth_system.services import email, cache_functions as cache
from django.core import exceptions
from rest_framework.settings import api_settings

User = get_user_model()


class RegisterCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'phone_or_email', 'full_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self.context['user'] = user
        if not user.is_phone:
            email.EmailActivation(self.context.get('request'), self.context).send([user.phone_or_email])
        else:
            email.phone_activation(self.context.get('user').phone_or_email)
        return user


class CheckActivationSerializer(serializers.Serializer):
    activation_code = serializers.IntegerField(write_only=True)
    phone_or_email = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if cache.getKey(attrs.get('phone_or_email')) != attrs.get('activation_code'):
            raise serializers.ValidationError({"invalid_code": "Invalid activate code for given user."})
        cache.deleteKey(attrs.get('phone_or_email'))
        return attrs


class SendEmailResetSerializer(serializers.Serializer):
    phone_or_email = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = User.objects.get(phone_or_email=attrs.get('phone_or_email'))
        if not user:
            raise serializers.ValidationError({"user": "User with given email does not exist."})
        self.context['user'] = user
        if not user.is_phone:
            email.EmailActivation(self.context.get('request'), self.context).send([user.phone_or_email])
        else:
            email.phone_activation(self.context.get('user').phone_or_email)
        return attrs


class PasswordResetConfirmSerializer(CheckActivationSerializer):
    new_password = serializers.CharField(max_length=150, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_or_email=attrs.get('phone_or_email'))
            password_validation.validate_password(attrs.get('new_password'), user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return super().validate(attrs)


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        try:
            user = CustomUser.objects.get(Q(username=username) | Q(phone_or_email=username))
        except CustomUser.DoesNotExist:
            user = None

        if user:
            attrs[self.username_field] = user.get_username()
            return super().validate(attrs)
        else:
            raise serializers.ValidationError("User not found")