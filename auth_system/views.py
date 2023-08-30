from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from auth_system.models import CustomUser
from auth_system.serializers import CustomUserSerializer, CheckActivationSerializer
from rest_framework import status


class CustomUserRegistrationView(CreateAPIView):
    serializer_class = CustomUserSerializer
    parser_classes = (FormParser, MultiPartParser)


class ActivationUserGenericAPIView(GenericAPIView):
    parser_classes = (FormParser, MultiPartParser)
    serializer_class = CheckActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(phone_or_email=serializer.validated_data.get('email'))
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(serializer.data, status=status.HTTP_200_OK)
