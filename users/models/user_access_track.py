from django.db import models


class UserAccessTrack(models.Model):
    user = models.OneToOneField(
        'User',
        related_name='user_access_tracks',
        on_delete=models.CASCADE,
    )
    sign_in_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True)
    failed_attempts = models.IntegerField(default=0)
    locked_at = models.DateTimeField(null=True)
    user_agent = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'user_access_tracks'
        verbose_name = 'user_access_track'
        verbose_name_plural = 'user_access_tracks'

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.save()

    def increase_sign_in_count(self):
        self.sign_in_count += 1
        self.save()
