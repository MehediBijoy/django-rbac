from django.db import models


class NotificationContent(models.Model):
    is_active = models.BooleanField(default=True)
    triggered_by = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=255, default='system')
    title = models.CharField(max_length=255)
    description = models.JSONField(null=True)
    notification_color = models.CharField(max_length=50, null=True)
    notification_icon = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_content'
        verbose_name = 'notification content'
        verbose_name_plural = 'notification contents'
