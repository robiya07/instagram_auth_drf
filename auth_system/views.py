from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser

from auth_system.serializers import CustomUserSerializer


class CustomUserRegistrationView(CreateAPIView):
    serializer_class = CustomUserSerializer
    parser_classes = (FormParser, MultiPartParser)