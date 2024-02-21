from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.helper import UserAuthResponse
from core.fields import OneTimePasswordField


class LoginSerializer(TokenObtainPairSerializer):
    mfa_code = OneTimePasswordField(auto_otp_validate=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: User | None = None

    def validate(self, attrs):
        super().validate(attrs)

        if self.user.google_mfa_activated and not self.user.verify_otp_token(attrs.get('mfa_code')):
            raise NotAuthenticated('Two factor authentication code invalid')

        return UserAuthResponse(self.user).data
