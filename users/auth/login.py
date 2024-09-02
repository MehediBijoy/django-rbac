from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from django.contrib.auth.models import update_last_login

from core.fields import CaptchaField
from users.helper import UserAuthResponse
from core.fields import OneTimePasswordField


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    captcha = CaptchaField(required=False)
    remember_me = serializers.BooleanField(default=False)
    mfa_code = OneTimePasswordField(auto_otp_validate=False, required=False)

    def validate(self, attrs):
        attrs["request"] = self.context["request"]
        user = authenticate(**attrs)

        if not user or not self.has_perm(user) or not user.is_active:
            raise exceptions.AuthenticationFailed

        if bool(
            user.is_otp_active and
            not user.verify_otp_token(attrs.get('mfa_code'))
        ):
            raise exceptions.AuthenticationFailed('Two factor authentication code invalid')

        # update user last login field
        update_last_login(None, user)

        return UserAuthResponse(
            user=user,
            remember_me=attrs.get('remember_me')
        ).data

    def has_perm(self, user):
        return user.is_user


class AdminLoginSerializer(LoginSerializer):
    def has_perm(self, user):
        return user.is_admin
