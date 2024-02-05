from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.exceptions import ValidationError

TOKEN_VALID_DURATION = 15


class ConfirmationMixin(models.Model):
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=255, null=True)
    confirmation_sent_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def sent_confirmation(self):
        self.confirmation_sent_at = timezone.now()
        self.confirmation_token = get_random_string(25)
        self.save(update_fields=['confirmation_sent_at', 'confirmation_token'])

        # add here email confirmation functionalities

    @property
    def is_confirmation_token_valid(self):
        if self.confirmation_sent_at is None:
            return False

        diff = timezone.now() - self.confirmation_sent_at
        return diff <= timedelta(minutes=TOKEN_VALID_DURATION)

    def confirm(self):
        if not self.is_confirmation_token_valid:
            raise ValidationError('confirmation token is expired')

        self.email_confirmed = True
        self.confirmation_token = None
        self.confirmation_sent_at = None
        self.save(update_fields=[
            'email_confirmed',
            'confirmation_sent_at',
            'confirmation_token']
        )
