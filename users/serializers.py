from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'user_type', 'status',
                  'status_reason', 'is_active', 'role', 'google_mfa_activated')
