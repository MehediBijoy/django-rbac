import json
from users.models import Notification, NotificationContent


class NotificationService:

    def __init__(self, payload):
        self.payload = json.dumps(payload)

    def notify(self, user, triggered_by):
        content, _ = NotificationContent.objects.get_or_create(
            triggered_by=triggered_by,
            notification_type='system',
            defaults={'title': 'Default Title'}
        )

        return self.create_notification(
            user=user,
            content_id=content.id
        )

    def create_notification(self, user, content_id):
        return Notification.objects.create(
            user=user,
            payload=self.payload,
            notification_content_id=content_id
        )
