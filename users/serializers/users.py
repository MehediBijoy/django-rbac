from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, UserAccessTrack


class AccessTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccessTrack
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(source='get_user_type_display')
    role = serializers.CharField(source='get_role_display')
    state = serializers.CharField(source='get_status_display')
    sign_in_count = serializers.IntegerField(
        source='user_access_tracks.sign_in_count'
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'user_type', 'state',
            'status_reason', 'is_active', 'role',
            'google_mfa_activated', 'sign_in_count', 'last_login',
        )


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
