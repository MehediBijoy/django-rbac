from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from .models import UserRole


class ReadOnlyAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS and
            request.user.role == UserRole.ADMIN
        )


class IsOwnerOrSuperAdmin(BasePermission):
    def has_object_permission(self, request: Request, view, obj):
        return bool(
            request.user.role == UserRole.SUPER_ADMIN
            or obj == request.user
        )
