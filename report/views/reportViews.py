from django.db.models.functions import ExtractHour
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from user.models import Trip
from ..serializers.reportSerializers import PeakHoursSerializer



class PeakHoursReportView(ListAPIView):
    serializer_class = PeakHoursSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle_type"]

    def get_queryset(self):
        qs = Trip.objects.filter(status="completed")

        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            qs = qs.filter(approved_at__range=[start_date, end_date])

        return (
            qs.annotate(hour=ExtractHour('approved_at'))
              .values('hour')
              .annotate(trip_count=Count('id'))
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        trip_data = {item['hour']: item['trip_count'] for item in queryset}

        full_hourly_data = [
            {'hour': hour, 'trip_count': trip_data.get(hour, 0)}
            for hour in range(24)
        ]

        sorted_data = sorted(full_hourly_data, key=lambda x: x['trip_count'], reverse=True)

        serializer = self.get_serializer(sorted_data, many=True)
        return Response(serializer.data)