from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, mixins, status

from users.models import Notification, NotificationContent
from users.serializers.notifications import NotificationSerializer, NotificationContentSerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = []
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            data={'success': True},
            status=status.HTTP_201_CREATED,
        )


class NotificationContentViewSet(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = NotificationContentSerializer
    queryset = NotificationContent.objects.all()


router = DefaultRouter()
router.register(r'', NotificationViewSet)
router.register(r'contents', NotificationContentViewSet)

urlpatterns = router.urls
