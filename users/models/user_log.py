from django.db import models


class UserLog(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='user_logs',
    )
    type = models.CharField(max_length=255)
    payload = models.JSONField(null=True)
    reference = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='reference_logs'
    )

    class Meta:
        verbose_name = 'User log'
        verbose_name_plural = 'User logs'
