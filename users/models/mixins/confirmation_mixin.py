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
    unconfirmed_email = models.EmailField(null=True)

    class Meta:
        abstract = True

    def send_email_confirmation(self):
        self.confirmation_sent_at = timezone.now()
        self.confirmation_token = get_random_string(25)
        self.save(update_fields=['confirmation_sent_at', 'confirmation_token'])

        self.send_mail()

    def resend_email_confirmation(self):
        self.__check_prepend_generation()
        self.send_email_confirmation()

    def email_change_request(self, email: str):
        if not self.email_confirmed:
            raise ValidationError('Please confirm your primary email first')

        self.__check_prepend_generation()
        self.unconfirmed_email = email
        self.save(update_fields=['unconfirmed_email'])

        self.send_email_confirmation()

    @property
    def is_confirmation_token_valid(self):
        if self.confirmation_sent_at is None:
            return False

        diff = timezone.now() - self.confirmation_sent_at
        return diff <= timedelta(minutes=TOKEN_VALID_DURATION)

    def confirm(self):
        if not self.is_confirmation_token_valid:
            raise ValidationError('confirmation token is expired')

        update_fields = []
        if bool(self.unconfirmed_email):
            self.email = self.unconfirmed_email
            self.unconfirmed_email = None

            update_fields.extend(['email', 'unconfirmed_email'])

        self.email_confirmed = True
        self.confirmation_token = None
        self.confirmation_sent_at = None

        update_fields.extend([
            'email_confirmed',
            'confirmation_sent_at',
            'confirmation_token'
        ])

        self.save(update_fields=update_fields)

    def send_mail(self):
        """
        If we have unconfirmed email Then email send to unconfirmed email
        otherwise send to regular email
        """

    def __check_prepend_generation(self):
        if self.is_confirmation_token_valid:
            raise ValidationError(
                'We already sent confirmation token to your email, Please wait %s minutes'
                % TOKEN_VALID_DURATION
            )
