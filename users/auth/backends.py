from rest_framework import exceptions
from rest_framework_simplejwt import authentication, exceptions
from rest_framework_simplejwt.tokens import Token, AccessToken

from users.models import JwtBlackList


MAX_ATTEMPTS = 5


class JWTAuthentication(authentication.JWTAuthentication):
    def get_validated_token(self, raw_token: bytes) -> Token:
        try:
            token = AccessToken(raw_token)  # type: ignore
        except exceptions.TokenError:
            raise exceptions.InvalidToken

        # check token has already in black listed
        if JwtBlackList.check_revoked(token):
            raise exceptions.InvalidToken

        return token
