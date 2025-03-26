from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView

from ..models import Role
from ..serializers.rolesSerializers import roleSerializer

class CreateRoles(CreateAPIView):
    '''
        create Role
    '''
    serializer_class = roleSerializer
    queryset = Role.objects.all()

class RetrieveUpdateDestroyRoles(RetrieveUpdateDestroyAPIView):
    '''
        create Role
    '''
    serializer_class = roleSerializer
    queryset = Role.objects.all()