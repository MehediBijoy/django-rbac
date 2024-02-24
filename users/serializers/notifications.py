from rest_framework import serializers

from users.models import Notification, NotificationContent


class NotificationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationContent
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    notification_content = NotificationContentSerializer(read_only=True)
    notification_content_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationContent.objects.all(),
        write_only=True
    )

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'is_read']
