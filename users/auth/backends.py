from django.utils import timezone
from users.models import User, AccessLog
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.backends import ModelBackend


class UserAuthModelBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User._default_manager.get_by_natural_key(email)
            self.tracks: AccessLog = user.tracks
        except User.DoesNotExist:
            User().set_password(password)
        else:
            self._check_locked()
            if not user.check_password(password):
                self._record_logs(request)
                self._attempts_left()
            return user

    def _record_logs(self, request):
        self.tracks.failed_attempts += 1
        self.tracks.ip_address = request.META.get('REMOTE_ADDR')
        if self.tracks.failed_attempts >= 3:
            self.tracks.locked_at = timezone.now()
        self.tracks.save()

    def _check_locked(self):
        if self.tracks.locked_at:
            raise NotAuthenticated(
                f'Too many attemps taken, account locked at {
                    self.tracks.locked_at
                }'
            )

    def _attempts_left(self):
        failed_attempts = self.tracks.failed_attempts

        if failed_attempts < 3:
            message = f'{2 - failed_attempts} attempts left'
        else:
            message = 'last attempt left'

        raise NotAuthenticated(
            f'Wrong password, {message}'
        )
