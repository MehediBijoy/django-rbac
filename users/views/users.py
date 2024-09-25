from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.mixins import ViewSetAccessControlMixin
from users.permissions import IsOwnerOrSuperAdmin
from users.serializers.users import UserSerializer, ChangeEmailSerializer


class UserViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ViewSetAccessControlMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperAdmin]

    # search_fields work for only ?search=example@email.com params
    search_fields = ['first_name', 'last_name', 'email']

    # searching_lookups_map work for field wise search
    # example ?email=example@email.com
    # also we can add more logics for searching
    search_fields_lookups_map = {
        'email': 'email__icontains'
    }

    admin_only_actions = ['list']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def email_change(self, request: Request, *args, **kwargs):
        user = self.get_object()

        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.email_change_request(serializer.validated_data['email'])

        user.write_log(
            log_type='change_email',
            reference=request.user
        )

        return Response('success')
