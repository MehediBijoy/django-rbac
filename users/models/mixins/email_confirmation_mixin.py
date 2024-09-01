from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from rest_framework.exceptions import ValidationError

TOKEN_VALID_DURATION = 5


class EmailConfirmationMixin(models.Model):
    email: str
    email_confirmed = models.BooleanField(default=False)
    email_confirmed_at = models.DateTimeField(null=True)
    email_confirmation_token = models.CharField(max_length=255, null=True)
    email_confirmation_sent_at = models.DateTimeField(null=True)
    email_candidate = models.EmailField(null=True)

    class Meta:
        abstract = True

    def send_email_confirmation(self):
        self.email_confirmation_sent_at = timezone.now()
        self.email_confirmation_token = get_random_string(25)
        self.save(update_fields=['email_confirmation_sent_at', 'email_confirmation_token'])

        self.__send_mail()

    def resend_email_confirmation(self):
        self.__check_prepend_generation()
        self.send_email_confirmation()

    def email_change_request(self, email: str):
        if not self.email_confirmed:
            raise ValidationError('Please confirm your primary email first')

        self.__check_prepend_generation()
        self.email_candidate = email
        self.save(update_fields=['email_candidate'])

        self.send_email_confirmation()

    def confirm(self):
        if not self.__is_token_valid:
            raise ValidationError('confirmation token is expired')

        update_fields = []
        if bool(self.email_candidate):
            self.email = self.email_candidate
            self.email_candidate = None

            update_fields.extend(['email', 'email_candidate'])

        self.email_confirmed = True
        self.email_confirmed_at = timezone.now()
        self.email_confirmation_token = None
        self.email_confirmation_sent_at = None

        update_fields.extend([
            'email_confirmed',
            'email_confirmed_at',
            'email_confirmation_token',
            'email_confirmation_sent_at'
        ])

        self.save(update_fields=update_fields)

    def __send_mail(self):
        message = EmailMessage(
            subject='Confirm your email',
            body=f'your confirmation token is {self.email_confirmation_token}',
            to=[self.email]
        )
        res = message.send(fail_silently=False)
        print(res)

    def __check_prepend_generation(self):
        if self.__is_token_valid:
            raise ValidationError(
                'We already sent confirmation token to your email, Please wait %s minutes'
                % TOKEN_VALID_DURATION
            )

    @property
    def __is_token_valid(self):
        if self.email_confirmation_sent_at is None:
            return False

        diff = timezone.now() - self.email_confirmation_sent_at
        return diff <= timedelta(minutes=TOKEN_VALID_DURATION)
