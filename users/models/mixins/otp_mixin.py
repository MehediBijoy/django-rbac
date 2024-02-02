import pyotp
from django.db import models

from config import ENV


class OneTimePasswordMixin(models.Model):
    google_secret = models.CharField(max_length=255, null=True)
    google_mfa_activated = models.BooleanField(default=False)

    def get_otp_uri(self) -> str:
        """
        Generate OTP provisioning URI.
        https://stefansundin.github.io/2fa-qr/ Test uri through the url
        """
        if not self.google_secret:
            self.google_secret = self.__get_secret()
            self.save(update_fields=['google_secret'])

        return self.__get_totp().provisioning_uri(name=self.email, issuer_name=ENV.title)

    def verify_otp_token(self, token: str) -> bool:
        """
        Verify OTP token.
        """
        if token is None or self.google_secret is None:
            return False

        return self.__get_totp().verify(token)

    def change_otp_state(self, token: str, active: bool = False) -> bool:
        """
        Switch OTP status.
        """
        if self.verify_otp_token(token):
            self.google_mfa_activated = active
            self.save(update_fields=['google_mfa_activated'])
            return True

        return False

    def __get_secret(self) -> str:
        """
        Generate a random OTP secret.
        """
        return pyotp.random_base32()

    def __get_totp(self) -> pyotp.TOTP:
        """
        Get TOTP object.
        """
        return pyotp.TOTP(self.google_secret)

    class Meta:
        abstract = True
