import pyotp
from django.db import models

from config import ENV


class OneTimePasswordMixin(models.Model):
    otp_secret = models.CharField(max_length=255, null=True)
    is_otp_active = models.BooleanField(default=False)

    def generate_otp_uri(self) -> str:
        """
        Generate OTP provisioning URI.
        https://stefansundin.github.io/2fa-qr/ Test uri through the url
        """
        if not self.otp_secret:
            self.otp_secret = self.__get_secret()
            self.save(update_fields=['otp_secret'])

        return self.__get_totp().provisioning_uri(name=self.email, issuer_name=ENV.title)

    def verify_otp(self, token: str) -> bool:
        """
        Verify OTP token.
        """
        if token is None or self.otp_secret is None:
            return False

        return self.__get_totp().verify(token)

    def switch_otp(self, token: str, active: bool = False) -> bool:
        """
        Switch OTP status.
        """
        if self.verify_otp(token):
            self.is_otp_active = active
            self.save(update_fields=['is_otp_active'])
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
        return pyotp.TOTP(self.otp_secret)

    class Meta:
        abstract = True
