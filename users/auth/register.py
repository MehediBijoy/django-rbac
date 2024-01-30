from typing import OrderedDict
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from users.models import User, UserType
from .login import LoginSerializer


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

    user_type = serializers.CharField(required=False, allow_null=True)

    def validate(self, attrs: OrderedDict):
        password_confirmation = attrs.pop('password_confirmation')

        if attrs.get('password') != password_confirmation:
            raise serializers.ValidationError(
                {"password_confirmation": "confirmed password did't matched"}
            )

        return super().validate(attrs)

    def validate_user_type(self, value: str):
        if not value:
            return None

        if not value.upper() in UserType.names:
            raise serializers.ValidationError(
                f'type should be one of [{", ".join(UserType.labels)}]'
            )

        return UserType[value.upper()]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        sign_in = LoginSerializer(
            data={'email': user.email,
                  'password': serializer.validated_data.get('password')
                  }, context=self.get_serializer_context()
        )

        sign_in.is_valid(raise_exception=True)

        return Response(data=sign_in.validated_data, status=status.HTTP_201_CREATED)
