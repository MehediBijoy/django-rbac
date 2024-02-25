from django.utils import timezone
from rest_framework import exceptions
from django.contrib.auth import backends
from rest_framework_simplejwt import authentication, exceptions
from rest_framework_simplejwt.tokens import Token, AccessToken

from users.models import User, UserStatus, JwtBlackList


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


class ModelBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        try:
            user = User._default_manager.get_by_natural_key(username)
            self.access_tracks = user.access_tracks
        except User.DoesNotExist:
            User().set_password(password)
            raise exceptions.AuthenticationFailed
        else:
            self._check_restriction(user)
            if not user.check_password(password):
                self._update_failed_tracks(request, user)

            self.__update_access_tracks(request)
            return user

    def __update_access_tracks(self, request):
        meta = self.__request_meta(request)

        self.access_tracks.reset_failed_attempts()
        self.access_tracks.increase_sign_in_count()
        self.access_tracks.user_agent = meta['user_agent']
        self.access_tracks.ip_address = meta['ip_address']
        self.access_tracks.save()

    def __request_meta(self, request) -> dict[str, str]:
        user_agent = request.META.get('HTTP_USER_AGENT')
        ip_address = request.META.get('REMOTE_ADDR')
        return {'user_agent': user_agent, 'ip_address': ip_address}

    def _update_failed_tracks(self, request, user):
        self.access_tracks.failed_attempts += 1
        if self.access_tracks.failed_attempts >= MAX_ATTEMPTS:
            self.access_tracks.locked_at = timezone.now()
        self.access_tracks.save()

        user.write_log(
            log_type='incorrect_password',
            payload={
                'failed_attempts': self.access_tracks.failed_attempts,
                **self.__request_meta(request)
            }
        )
        self._attempts_left()

    def _attempts_left(self):
        self._check_locked()

        left_attempts = MAX_ATTEMPTS - self.access_tracks.failed_attempts
        message = '{} attempts left'.format(
            left_attempts if left_attempts > 1 else 'last'
        )

        raise exceptions.AuthenticationFailed(
            f'Wrong password, {message}'
        )

    def _check_locked(self):
        if self.access_tracks.locked_at:
            raise exceptions.PermissionDenied(
                f'Too many attempts taken, account locked at {self.access_tracks.locked_at}'
            )

    def _check_restriction(self, user: User):
        self._check_locked()

        if user.status == UserStatus.BLOCKED:
            raise exceptions.PermissionDenied('account is blocked')
