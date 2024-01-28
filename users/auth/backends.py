import bcrypt
from django.utils import timezone
from django.contrib.auth.backends import ModelBackend
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.hashers import make_password

from users.models import User, UserStatus

MAX_ATTEMPTS = 5


class UserAuthModelBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user: User = User._default_manager.get_by_natural_key(email)
            self.access_tracks = user.access_tracks
        except User.DoesNotExist:
            User().set_password(password)
        else:
            self._password_transfer(user, password)
            self._check_locked()
            self._update_attempt_meta(request)
            if not user.check_password(password):
                self._update_failed_attempts()
                self._attempts_left()

            self._check_restriction(user)
            self.access_tracks.reset_failed_attempts()
            self.access_tracks.increase_sign_in_count()
            return user

    def _update_attempt_meta(self, request):
        self.access_tracks.user_agent = request.META.get('HTTP_USER_AGENT')
        self.access_tracks.ip_address = request.META.get('REMOTE_ADDR')
        self.access_tracks.save()

    def _update_failed_attempts(self):
        self.access_tracks.failed_attempts += 1
        if self.access_tracks.failed_attempts >= MAX_ATTEMPTS:
            self.access_tracks.locked_at = timezone.now()
        self.access_tracks.save()

    def _check_locked(self):
        if self.access_tracks.locked_at:
            raise NotAuthenticated(
                f'Too many attempts taken, account locked at {self.access_tracks.locked_at}'
            )

    def _attempts_left(self):
        self._check_locked()

        left_attempts = MAX_ATTEMPTS - self.access_tracks.failed_attempts

        if left_attempts > 1:
            message = f'{left_attempts} attempts left'
        else:
            message = 'last attempt left'

        raise NotAuthenticated(
            f'Wrong password, {message}'
        )

    def _check_restriction(self, user: User):
        if user.status == UserStatus.BLOCKED:
            raise NotAuthenticated('account is blocked')

    def _password_transfer(self, user: User, password: str):
        if not user.deprecated_password:
            return

        encoded_pass = password.encode()
        existing_password = user.deprecated_password.encode()
        if bcrypt.checkpw(encoded_pass, existing_password):
            user.password = make_password(password)
            user.deprecated_password = None
            user.save()
