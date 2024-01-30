from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from users.models import User


class OneTimePasswordValidator:
    requires_context = True

    def __call__(self, value, serializer_field):
        user: User = serializer_field.context['request'].user
        if not user.verify_otp(value):
            raise serializers.ValidationError(_('2FA code is invalid'))


class OneTimePasswordField(serializers.CharField):
    def __init__(self, auto_otp_validate=True, *args, **kwargs):
        kwargs.setdefault('min_length', 6)
        kwargs.setdefault('max_length', 6)
        kwargs.setdefault('write_only', True)

        if auto_otp_validate:
            validators: list = kwargs.get('validators', [])
            validators.append(OneTimePasswordValidator())
            kwargs['validators'] = validators

        super().__init__(*args, **kwargs)
