from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser
from auth_system.services.email import ActivationEmail
from auth_system.constants import Messages
from auth_system.services.cache_functions import getKey, deleteKey, setKey
import random

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
        print(attrs.get('phone_or_email'), attrs.get('activation_code'))
        if getKey(attrs.get('phone_or_email')) != attrs.get('activation_code'):
            raise serializers.ValidationError({"invalid_code": error_messages.INVALID_ACTIVATE_CODE_ERROR})
        deleteKey(attrs.get('phone_or_email'))
        return attrs
