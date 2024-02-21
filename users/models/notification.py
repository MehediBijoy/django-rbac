from django.db import models
from django.utils import timezone

from .notification_content import NotificationContent


class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    payload = models.JSONField(null=True)
    delivery_at = models.DateTimeField(default=timezone.now)
    notification_content = models.ForeignKey(NotificationContent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
