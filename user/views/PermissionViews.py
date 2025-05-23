from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView

from ..models import Permission
from ..serializers.permissionSerializers import permissionsSerializer


class CreatePermission(CreateAPIView):
    '''
        create Permission
    '''
    serializer_class = permissionsSerializer
    queryset = Permission.objects.all()


class RetrieveUpdateDestroyPermission(RetrieveUpdateDestroyAPIView):
    '''
        create Permission
    '''
    serializer_class = permissionsSerializer
    queryset = Permission.objects.all()

