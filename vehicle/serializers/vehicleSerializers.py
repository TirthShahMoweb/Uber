from django.urls import reverse

from rest_framework import serializers

from ..models import Vehicle
from user.models import DriverDetail



class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)

    def create(self, validated_data):
        user = self.context['user']
        try:
            driver = DriverDetail.objects.get(user=user)
        except DriverDetail.DoesNotExist:
            raise serializers.ValidationError("Driver details not found for this user.")


        vehicle = Vehicle.objects.create(driver=driver, **validated_data)
        return vehicle


class VerificationPendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'vehicle_image', 'vehicle_rc', 'vehicle_type',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['approval_url'] = reverse('vehicle-verification-approval', args=[instance.id])
        return representation


class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)

class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)


class DisplayVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        # fields = '__all__'
        fields = ('id','driver','vehicle_image', 'vehicle_rc', 'vehicle_type',)

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context['request']
    #     representation['vehicle_url'] = reverse('Select_vehicle', args=[instance.id])
    #     return representation