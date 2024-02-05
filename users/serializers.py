from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(source='get_user_type_display')
    role = serializers.CharField(source='get_role_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = User
        fields = ('id', 'email', 'user_type', 'status',
                  'status_reason', 'is_active', 'role', 'google_mfa_activated')


class ChangeEmailSerializer(serializers.Serializer):
    """
    Todo: We need to validate unconfirmed email too for unique
    """
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Email already exists'
            )
        ]
    )
