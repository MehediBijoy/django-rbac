from rest_framework import permissions

from .models import UserRole


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.SUPER_ADMIN


class IsSafeAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS and
            request.user.role == UserRole.ADMIN
        )


IsSafeOrSuperAdmin = IsSuperAdmin | IsSafeAdmin


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_user


class IsOwnerOrSuperAdmin(IsSafeAdmin):
    def has_permission(self, request, view):
        if request.user.role == UserRole.ADMIN:
            return super().has_permission(request, view)

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.SUPER_ADMIN:
            return True

        return obj == request.user
