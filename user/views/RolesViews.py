from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)

from ..models import Role
from ..serializers.rolesSerializers import roleListSerializer, roleSerializer


class CreateRoles(CreateAPIView):
    """
    create Role
    """

    serializer_class = roleSerializer
    queryset = Role.objects.all()


class RetrieveUpdateDestroyRoles(RetrieveUpdateDestroyAPIView):
    """
    create Role
    """

    serializer_class = roleSerializer
    queryset = Role.objects.all()


class RoleListView(ListAPIView):
    """
    List all roles
    """

    serializer_class = roleListSerializer
    queryset = Role.objects.exclude(role_name="CEO")
