from rest_framework import serializers
from user.models import Trip


class PeakHoursSerializer(serializers.Serializer):
    trip_count = serializers.IntegerField()
    hour = serializers.IntegerField()