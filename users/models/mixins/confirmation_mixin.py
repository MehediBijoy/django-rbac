from django.db import models


class ConfirmationMixin(models.Model):
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=255, null=True)
    confirmation_sent_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
