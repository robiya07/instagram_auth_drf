from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser
from auth_system.services.email import ActivationEmail
from auth_system.constants import Messages
from auth_system.services.cache_functions import getKey, deleteKey

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
        return user


class CheckActivationSerializer(serializers.Serializer):
    activation_code = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        if getKey(attrs.get('email')) != attrs.get('activation_code'):
            raise serializers.ValidationError({"invalid_code": error_messages.INVALID_ACTIVATE_CODE_ERROR})
        deleteKey(attrs.get('email'))
        return attrs
