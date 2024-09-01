from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from users.models import User
from users.helper import UserAuthResponse


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(), message='Email already exist')
        ]
    )

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password',
               'placeholder': 'password confirmation'}
    )

    def validate(self, attrs: dict):
        password_confirmation = attrs.pop('password_confirmation')

        if attrs.get('password') != password_confirmation:
            raise serializers.ValidationError(
                {"password_confirmation": "confirmed password didn't matched"}
            )

        return super().validate(attrs)

    def create(self, validated_data) -> User:
        return User.objects.create_user(**validated_data)


class RegisterAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # sent confirmation token to user though email
        user.send_email_confirmation()

        return Response(
            data=UserAuthResponse(user=user).data,
            status=status.HTTP_201_CREATED,
        )
