from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperAdmin, IsSafeOrSuperAdmin


class ViewSetAccessControlMixin:
    admin_only_actions = []
    super_admin_only_action = []
    unauthorized_actions = []

    admin_permission_classes = [IsAuthenticated, IsSafeOrSuperAdmin]
    super_admin_permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_permissions(self):
        if self.action in self.unauthorized_actions:
            return []

        if self.action in self.super_admin_only_action:
            return [perm() for perm in self.super_admin_permission_classes]

        if self.action in self.admin_only_actions:
            return [perm() for perm in self.admin_permission_classes]

        return super().get_permissions()
