from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, UserAccessTrack


class AccessTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccessTrack
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'status', 'status_reason',
            'is_active', 'role', 'is_otp_active', 'last_login',
        )


class ChangeEmailSerializer(serializers.Serializer):
    """
    Todo: We need to validate unconfirmed email too for unique
    """
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup='iexact',
                message='Email already exists'
            )
        ]
    )

    def validate_email(self, value: str):
        return str(value).lower() if value else value
