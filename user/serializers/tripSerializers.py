from rest_framework import serializers
from rest_framework.exceptions import APIException
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import Trip, User, DriverDetail



class CustomValidationError(APIException):
    status_code = 400
    default_detail = "Validation Error"

    def __init__(self, errors, message="Validation Error"):
        self.detail = {
            "status": "error",
            "message": message,
            "errors": errors
        }


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ('drop_location_latitude', 'drop_location_longitude', 'vehicle_type', 'pickup_location_latitude', 'pickup_location_longitude', 'pickup_location', 'drop_location', 'distance', 'estimated_time', 'fare',)

    def validate(self, data):
        user = self.context['user']
        if not User.objects.filter(id=user.id, user_type='customer').exists():
            errors = {"user": "Only rider can do this action! if Registered."}
            raise CustomValidationError(errors)

        required_fields = [
            'drop_location_latitude',
            'drop_location_longitude',
            'pickup_location_latitude',
            'pickup_location_longitude',
            'pickup_location',
            'drop_location',
            'distance',
            'estimated_time',
            'fare',
            'vehicle_type',
        ]

        for field in required_fields:
            if not data.get(field):
                raise CustomValidationError({field: f"{field} is required."})

        return data


    def create(self, validated_data):
        user = self.context.get('user')
        trip = Trip.objects.create(customer=user, **validated_data)
        return trip


class TripCancelSerializer(serializers.ModelSerializer):
    cancel_by = serializers.CharField(required=False)

    class Meta:
        model = Trip
        fields = ('description', 'cancel_by')

    def validate(self, attrs):
        if self.context.get('user').user_type == 'admin':
            errors = {"user_type": "Only customer and driver can cancel this Trip."}
            raise CustomValidationError(errors)

        if self.context.get('user').user_type == 'driver':
            trip_instance = self.instance
            if trip_instance.status == "cancelled":
                errors = {"user_type": "This trip is already cancelled."}
                raise CustomValidationError(errors)
            print(trip_instance.status,"1234312343234")

            if trip_instance.status != "Accepted":
                errors = {"user_type": "At this moment you can't cancel the Trip."}
                raise CustomValidationError(errors)
        return attrs

    def update(self, instance, attrs):
        user = self.context.get('user')
        instance.status = 'cancelled'
        instance.description = attrs['description']
        if attrs.get('cancel_by'):
            instance.cancelled_by = 'auto'
        else:
            instance.cancelled_by = 'customer' if user.user_type == "customer" else "driver"
        instance.cancelled_at = timezone.now()
        instance.save()
        return instance


class TripApprovalSerializer(serializers.Serializer):

    def validate(self, attrs):
        if self.context.get('user').user_type != 'driver':
            errors = {"user_type": "Only driver can approve this Trip."}
            raise CustomValidationError(errors)

        if self.context.get('user').user_type == 'driver':
            trip_instance = self.instance
            print(trip_instance.status)
            if trip_instance.status != "pending":
                errors = {"user_type": "Trip has been already accepted."}
                raise CustomValidationError(errors)
        return attrs

    def update(self, instance, attrs):
        user = self.context.get('user')
        driver = get_object_or_404(DriverDetail, user=user)
        instance.driver = user
        instance.vehicle_id = driver.in_use
        instance.status = "Accepted"
        instance.save()
        return instance