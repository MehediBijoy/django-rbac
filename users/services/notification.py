import json
from django.core.serializers.json import DjangoJSONEncoder
from users.models import Notification, NotificationContent


class NotificationService:
    @classmethod
    def notify(cls, user, triggered_by, payload):
        content, _ = NotificationContent.objects.get_or_create(
            triggered_by=triggered_by,
            notification_type='system',
            defaults={'title': 'Default Title'}
        )

        return cls().create_manual_notification(
            user=user,
            content_id=content.id,
            payload=payload
        )

    def create_manual_notification(self, user, content_id, payload):
        return Notification.objects.create(
            user=user,
            payload=json.dumps(payload, cls=DjangoJSONEncoder),
            notification_content_id=content_id
        )
