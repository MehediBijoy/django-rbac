from django.db import models


class UserLog(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='user_log',
    )
    type = models.CharField(max_length=255)
    payload = models.JSONField(null=True)
    reference = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='reference_log'
    )

    class Meta:
        db_table = 'user_log'
        verbose_name = 'User log'
        verbose_name_plural = 'User logs'
