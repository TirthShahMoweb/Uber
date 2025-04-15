# from django.urls import reverse

# from rest_framework import serializers

# from ..models import Vehicle, VehicleRequest
# from user.models import DriverDetail



# class VehicleSerializer(serializers.ModelSerializer):
#     vehicle_front_image = serializers.ImageField(required=True)
#     vehicle_back_image = serializers.ImageField(required=True)
#     vehicle_leftSide_image = serializers.ImageField(required=True)
#     vehicle_rightSide_image = serializers.ImageField(required=True)
#     vehicle_rc_front_image = serializers.ImageField(required=True)
#     vehicle_rc_back_image = serializers.ImageField(required=True)

#     class Meta:
#         model = VehicleRequest
#         fields = ('vehicle_number', 'vehicle_type', 'vehicle_type',)

#     def create(self, validated_data):
#         user = self.context['user']
#         try:
#             driver = DriverDetail.objects.get(user=user)
#         except DriverDetail.DoesNotExist:
#             raise serializers.ValidationError("Driver details not found for this user.")


#         vehicle = VehicleRequest.objects.create(driver=driver, **validated_data)
#         return vehicle


# class VehicleVerificationPendingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         fields = ('id', 'vehicle_image', 'vehicle_rc', 'vehicle_type',)

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['approval_url'] = reverse('vehicle-verification-approval', args=[instance.id])
#         return representation


# class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)

# class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)


# class DisplayVehicleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         # fields = '__all__'
#         fields = ('id','driver','vehicle_image', 'vehicle_rc', 'vehicle_type',)

#     # def to_representation(self, instance):
#     #     representation = super().to_representation(instance)
#     #     request = self.context['request']
#     #     representation['vehicle_url'] = reverse('Select_vehicle', args=[instance.id])
#     #     return representation