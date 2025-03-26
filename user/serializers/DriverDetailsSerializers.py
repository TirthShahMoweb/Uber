from django.urls import reverse

from rest_framework import serializers

from ..models import DriverDetail



class VerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDetail
        fields = ('aadhar_photo', 'licence_number', 'dob', 'lang',)

    def validate(self, data):
        if DriverDetail.objects.filter(user=self.context['user']).exists():
            raise serializers.ValidationError("You have already applied as a driver. You cannot apply again.")
        return data


class VerificationPendingSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField()
    profile_pic = serializers.ImageField(source = 'user.profile_pic')

    class Meta:
        model = DriverDetail
        fields = ('id', 'driver_name', 'aadhar_photo' , 'profile_pic', 'licence_number' ,'dob')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['approval_url'] = reverse('driver-verification-approval', args=[instance.id])
        return representation

class ResubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriverDetail
        fields = ('aadhar_photo', 'licence_number', 'dob',)