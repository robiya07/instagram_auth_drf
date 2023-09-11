from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from auth_system.models import User as UserModel, UserConfirmation, VIA_EMAIL, VIA_PHONE
from auth_system.services import email
from django.utils import timezone
from django.core import exceptions
from rest_framework.settings import api_settings

from auth_system.utils import email_phone

User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150, write_only=True)
    email_phone = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = UserModel
        fields = ['id', 'email_phone', 'full_name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        attrs['first_name'] = attrs['full_name'].split(' ')[0]
        attrs['last_name'] = attrs.pop('full_name').split(' ')[1]
        t = attrs.pop('email_phone')
        print(type(t))
        attrs['phone_number'] = email_phone(t)['phone_number']
        attrs['email'] = email_phone(t)['email']
        if not attrs['email'] and not attrs['phone_number']:
            raise serializers.ValidationError(email_phone(t)['email_phone'])
        attrs['auth_type'] = VIA_PHONE if attrs['phone_number'] else VIA_EMAIL
        return attrs


class VerifyCodeSerializer(serializers.Serializer):
    email_phone = serializers.CharField(max_length=150, write_only=True)
    code = serializers.CharField(max_length=4, write_only=True)

    def validate(self, attrs):
        email_phone = attrs.get('email_phone')
        activation_code = attrs.get('code')
        try:
            user = User.objects.get(Q(email=email_phone) | Q(phone_number=email_phone))
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"email_phone": "User with given email or phone does not exist."})
        try:
            UserConfirmation.objects.get(user=user, code=activation_code)
        except UserConfirmation.DoesNotExist:
            raise serializers.ValidationError({"activation_code": "Invalid activation code."})
        return attrs


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        try:
            user = UserModel.objects.get(Q(username=username) | Q(email=username) | Q(phone_number=username))
            self.context['user'] = user
        except UserModel.DoesNotExist:
            user = None

        if user:
            attrs[self.username_field] = user.get_username()
            return super().validate(attrs)
        else:
            raise serializers.ValidationError("User not found")


class SendEmailResetSerializer(serializers.Serializer):
    email_phone = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = User.objects.get(Q(email=attrs.get('email_phone')) | Q(phone_number=attrs.get('email_phone')))
        if not user:
            raise serializers.ValidationError({"user": "User with given email or phone does not exist."})
        self.context['user'] = user
        if user.email:
            code = user.create_verify_code(VIA_EMAIL)
            email.EmailActivation(self.context.get('request'), self.context, activation_code=code).send([user.email])
        else:
            code = user.create_verify_code(VIA_PHONE)
            email.phone_activation(user.phone_number, code)
        return attrs


class PasswordResetConfirmSerializer(VerifyCodeSerializer):
    new_password = serializers.CharField(max_length=150, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(Q(email=attrs.get('email_phone')) | Q(phone_number=attrs.get('email_phone')))
            self.context['user'] = user
            validate_password(attrs.get('new_password'), user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return super().validate(attrs)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=150, write_only=True)
    new_password = serializers.CharField(max_length=150, write_only=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        user = self.context['request'].user

        if not user.check_password(old_password):
            raise serializers.ValidationError('Incorrect old password')
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return attrs
