from rest_framework.permissions import BasePermission

from user.models import RolePermission


class DynamicPermission(BasePermission):
    """
        DynamicPermission for all types of permissions.
    """
    def __init__(self, required_permissions):
        self.required_permissions = required_permissions

    def has_permission(self, request, view):
        role = request.user.role
        if role is None:
            return False
        if request.user.user_type != 'admin':
            return False
        permissions = RolePermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = self.required_permissions
        return bool(required_permissions in list(permissions))