from decouple import config
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ENV:
    TITLE = 'Django RBAC'
    SECRET_KEY = config('SECRET_KEY')

    TURNSTILE_SECRET = config('TURNSTILE_SECRET')
    SES_ACCESS_KEY = config('SES_ACCESS_KEY')
    SES_SECRET_KEY = config('SES_SECRET_KEY')
    SES_REGION_NAME = config('SES_REGION_NAME')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
