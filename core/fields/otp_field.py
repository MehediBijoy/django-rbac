from rest_framework import serializers

from users.models import User


class OneTimePasswordValidator:
    requires_context = True

    def __call__(self, value, serializer_field):
        user: User = serializer_field.context['request'].user
        if not user.verify_otp(value):
            raise serializers.ValidationError(
                {'mfa_code': '2FA code is invalid'}
            )


class OneTimePasswordFiled(serializers.CharField):
    def __init__(self, auto_otp_validate=True, *args, **kwargs):
        kwargs.setdefault('min_length', 6)
        kwargs.setdefault('max_length', 6)
        kwargs.setdefault('write_only', True)
        kwargs.setdefault('required', False)

        if auto_otp_validate:
            validators: list = kwargs.get('validators', [])
            validators.append(OneTimePasswordValidator())
            kwargs['validators'] = validators

        super().__init__(*args, **kwargs)
