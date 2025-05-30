from rest_framework import serializers
from user.models import Trip


class PeakHoursSerializer(serializers.ModelSerializer):
    trip_count = serializers.IntegerField()
    hour = serializers.IntegerField()

    class Meta:
        model = Trip
        fields = ( 'trip_count', 'hour', )