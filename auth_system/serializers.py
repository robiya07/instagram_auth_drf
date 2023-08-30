from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser
from auth_system.services.email import ActivationEmail


User = get_user_model()


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
