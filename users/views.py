from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from .models import User
from .mixins import RoleBasedAccessControlMixin
from .serializers import UserSerializer, ChangeEmailSerializer
from .permissions import IsOwnerOrSuperAdmin


class UserViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    RoleBasedAccessControlMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperAdmin]

    admin_only_actions = ['list']

    @action(detail=True, methods=['post'])
    def email_change(self, request: Request, *args, **kwargs):
        user = self.get_object()

        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.email_change_request(serializer.validated_data['email'])

        return Response('success')
