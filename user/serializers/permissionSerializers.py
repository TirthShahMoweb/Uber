from rest_framework import serializers
from ..models import Permission



class permissionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ['permission_name', 'description']

    def validate_permission_name(self, data):

        if Permission.objects.filter(permission_name = data).exists():
            raise serializers.ValidationError("Permission name already exists.")
        return data

    def create(self, validated_data):
        permission = Permission.objects.create(**validated_data)
        return permission