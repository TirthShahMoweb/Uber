from rest_framework.generics import ListAPIView
from django.db.models.functions import ExtractHour
from django.db.models import Count
from user.models import Trip

from ..serializers.reportSerializers import PeakHoursSerializer



class PeakHoursReportView(ListAPIView):
    ...
    serializer_class = PeakHoursSerializer

    def get_queryset(self):
        hourly_approved_trips = (
            Trip.objects
            .filter(approved_at__isnull=False)
            .annotate(hour=ExtractHour('approved_at'))
            .values('hour')
            .annotate(trip_count=Count('id'))
            .order_by('hour'))

        return hourly_approved_trips