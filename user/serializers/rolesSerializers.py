from rest_framework import serializers

from ..models import Role


class roleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ("role_name", "description")

    def validate_role_name(self, data):

        if Role.objects.filter(role_name=data).exists():
            raise serializers.ValidationError("Role name already exists.")
        return data

    def create(self, validated_data):
        role = Role.objects.create(**validated_data)
        return role


class roleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ("id", "role_name")
