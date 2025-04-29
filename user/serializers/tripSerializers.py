from rest_framework import serializers
from rest_framework.exceptions import APIException

from ..models import Trip, User



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
        print(validated_data,"----------------------------------------------")
        trip = Trip.objects.create(customer=user, **validated_data)
        return validated_data