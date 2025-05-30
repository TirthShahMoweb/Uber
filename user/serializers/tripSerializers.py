import random

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ..models import DriverDetail, Payment, Trip, User


class CustomValidationError(APIException):
    status_code = 400
    default_detail = "Validation Error"

    def __init__(self, errors, message="Validation Error"):
        self.detail = {"status": "error", "message": message, "errors": errors}


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = (
            "drop_location_latitude",
            "drop_location_longitude",
            "vehicle_type",
            "pickup_location_latitude",
            "pickup_location_longitude",
            "pickup_location",
            "drop_location",
            "distance",
            "estimated_time",
            "fare",
        )

    def validate(self, data):
        user = self.context["user"]
        if not User.objects.filter(id=user.id, user_type="customer").exists():
            errors = {"user": "Only rider can do this action! if Registered."}
            raise CustomValidationError(errors)

        required_fields = [
            "drop_location_latitude",
            "drop_location_longitude",
            "pickup_location_latitude",
            "pickup_location_longitude",
            "pickup_location",
            "drop_location",
            "distance",
            "estimated_time",
            "fare",
            "vehicle_type",
        ]

        for field in required_fields:
            if not data.get(field):
                raise CustomValidationError({field: f"{field} is required."})

        return data

    def create(self, validated_data):
        user = self.context.get("user")
        trip = Trip.objects.create(customer=user, **validated_data)
        return trip


class TripCancelSerializer(serializers.ModelSerializer):
    cancel_by = serializers.CharField(required=False)

    class Meta:
        model = Trip
        fields = ("cancelation_description", "cancel_by")

    def validate(self, attrs):
        if self.context.get("user").user_type == "admin":
            errors = {"user_type": "Only customer and driver can cancel this Trip."}
            raise CustomValidationError(errors)

        if self.context.get("user").user_type == "driver":
            trip_instance = self.instance
            if trip_instance.status == "cancelled":
                errors = {"user_type": "This trip is already cancelled."}
                raise CustomValidationError(errors)

            if trip_instance.status != "Accepted":
                errors = {"user_type": "At this moment you can't cancel the Trip."}
                raise CustomValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        user = self.context.get("user")
        instance.status = "cancelled"
        instance.cancelation_description = validated_data["cancelation_description"]
        if validated_data.get("cancel_by"):
            instance.cancelled_by = "auto"
        else:
            instance.cancelled_by = (
                "customer" if user.user_type == "customer" else "driver"
            )
        instance.cancelled_at = timezone.now()
        instance.save()
        return instance


class TripApprovalSerializer(serializers.Serializer):

    def validate(self, attrs):
        if self.context.get("user").user_type != "driver":
            errors = {"user_type": "Only driver can approve this Trip."}
            raise CustomValidationError(errors)

        if self.context.get("user").user_type == "driver":
            trip_instance = self.instance
            if trip_instance.status != "pending":
                errors = {"user_type": "Trip has been already accepted."}
                raise CustomValidationError(errors)
        return attrs

    def update(self, instance, attrs):
        user = self.context.get("user")
        driver = get_object_or_404(DriverDetail, user=user)
        instance.driver = user
        instance.vehicle_id = driver.in_use
        instance.status = "accepted"
        instance.approved_at = timezone.now()
        instance.otp = random.randint(1000, 9999)
        instance.save()
        return instance


class VerifiedDriverAtPickUpLocationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        otp = attrs.get("otp")
        trip = self.context.get("trip")

        if not otp.isdigit():
            errors = {"otp": "OTP must contain only numeric characters."}
            raise CustomValidationError(errors)

        if len(otp) != 4:
            errors = {"otp": "OTP must be exactly 4 digits long."}
            raise CustomValidationError(errors)

        otp = int(otp)

        if trip.otp != otp:
            errors = {"otp": "Invalid OTP."}
            raise CustomValidationError(errors)
        return attrs


class FeedbackRatingSerializer(serializers.Serializer):
    feedback = serializers.CharField(required=True)
    rating = serializers.IntegerField(required=True)

    def validate(self, attrs):
        user = self.context.get("user")
        trip = self.context.get("trip")
        if 0 >= attrs.get("rating") or attrs.get("rating") >= 6:
            errors = {"rating": "Should be between 1 to 5."}
            raise CustomValidationError(errors)

        if user != trip.customer and user != trip.driver:
            errors = {"user": "User is not the customer or driver of this trip."}
            raise CustomValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        user = self.context.get("user")
        if user == instance.customer:
            instance.driver_feedback = validated_data.get("feedback")
            instance.driver_rating = validated_data.get("rating")

        elif user == instance.driver:
            instance.customer_feedback = validated_data.get("feedback")
            instance.customer_rating = validated_data.get("rating")

        instance.save()
        return validated_data


class PaymentListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="trip.driver.first_name")
    last_name = serializers.CharField(source="trip.driver.last_name")

    class Meta:
        model = Payment
        fields = ("id", "trip_id", "first_name", "last_name", "amount", "status")


from django.conf import settings


class DriverPersonalInfoSerializer(serializers.ModelSerializer):
    thumbnail_pic = serializers.ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ("id", "thumbnail_pic", "mobile_number")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Extract full request context
        request_context = self.context.get("server")

        base_url = f"{"http"}://{request_context[0]}:{request_context[1]}"  # Construct base URL

        if instance.thumbnail_pic:
            representation["thumbnail_pic"] = f"{base_url}{instance.thumbnail_pic.url}"

        return representation
