from rest_framework import serializers

from users.models import Notification, NotificationContent


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationContent
        fields = '__all__'
