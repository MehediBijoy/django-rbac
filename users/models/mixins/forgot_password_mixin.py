from django.db import models

TOKEN_VALID_DURATION = 5


class ForgotPasswordMixin(models.Model):
    forgot_password_token = models.CharField(max_length=255, null=True, unique=True)
    forgot_password_token_sent_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
