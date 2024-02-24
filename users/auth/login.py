from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers, exceptions

from users.helper import UserAuthResponse
from core.fields import CaptchaField
from core.fields import OneTimePasswordField


class LoginSerializer(serializers.Serializer):
    default_error_messages = {
        "no_active_account": "No active account found with the given credentials"
    }

    email = serializers.EmailField()
    password = serializers.CharField()
    mfa_code = OneTimePasswordField(auto_otp_validate=False, required=False)
    captcha = CaptchaField(required=False)

    def validate(self, attrs):
        try:
            attrs["request"] = self.context["request"]
        except KeyError:
            pass

        user = authenticate(**attrs)

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        if not self.has_perm(user):
            raise exceptions.AuthenticationFailed

        if bool(
                user.google_mfa_activated and
                not user.verify_otp_token(attrs.get('mfa_code'))
        ):
            raise exceptions.AuthenticationFailed('Two factor authentication code invalid')

        # update user last login field
        update_last_login(None, user)

        log = user.access_tracks
        user.write_log(
            log_type='login',
            payload={
                'sign_in_count': log.sign_in_count,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
            }
        )

        return UserAuthResponse(user).data

    def has_perm(self, user):
        return user.is_user


class AdminLoginSerializer(LoginSerializer):
    def has_perm(self, user):
        return user.is_admin
