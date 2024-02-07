from os import getenv
from dataclasses import dataclass


@dataclass(frozen=True)
class ENV:
    title = 'Bretton Woods Gold'

    TURNSTILE_SECRET = getenv('TURNSTILE_SECRET')
