from rest_framework import permissions

from ..permissions import IsSafeAdmin, IsSuperAdmin


class ViewsetAccessControlMixin:
    admin_only_actions: list[str] = []
    super_admin_only_action: list[str] = []
    unauthorized_actions: list[str] = []

    admin_permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsSafeAdmin,
    ]
    super_admin_permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin,
    ]

    def get_permissions(self):
        if self.action in self.unauthorized_actions:
            return []

        if self.action in self.super_admin_only_action:
            return [perm() for perm in self.super_admin_permission_classes]

        if self.action in self.admin_only_actions:
            return [perm() for perm in self.admin_permission_classes]

        return super().get_permissions()
