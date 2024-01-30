from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from core.fields import OneTimePasswordField


class LoginSerializer(TokenObtainPairSerializer):
    mfa_code = OneTimePasswordField(auto_otp_validate=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: User = None

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.google_mfa_activated:
            return data

        if not self.user.verify_otp_token(attrs.get('mfa_code')):
            raise NotAuthenticated(code='005', detail='MFA code invalid')

        return data
