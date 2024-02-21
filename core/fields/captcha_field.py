import requests
from rest_framework import serializers
from dataclasses import dataclass, asdict
from requests.exceptions import RequestException

from config import ENV


@dataclass
class TurnstileVerifyRequest:
    secret: str
    response: str
    remoteip: str | None

    def dict(self) -> dict[str, str]:
        return asdict(self)


class TurnstileCaptchaValidator:
    def __init__(self):
        self.url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    def __call__(self, token: str):
        response = self.verify(token)

        if not response['success']:
            raise serializers.ValidationError(
                'captcha verification field, Please try again'
            )

        return True

    def verify(self, token: str) -> dict:
        model = TurnstileVerifyRequest(
            secret=ENV.TURNSTILE_SECRET,
            response=token,
            remoteip=None,
        )

        default_response = {
            'success': False,
            'error-codes': [],
        }

        try:
            response = requests.post(self.url, model.dict())
        except RequestException:
            return default_response
        else:
            if response.status_code != 200:
                return default_response

            """
            Here we merge with default response
            original response merge with default_response
            otherwise keep as it is
            """
            default_response.update(response.json())

            return default_response


class CaptchaField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('write_only', True)

        validators: list = kwargs.get('validators', [])
        validators.append(TurnstileCaptchaValidator())
        kwargs['validators'] = validators

        super().__init__(**kwargs)
