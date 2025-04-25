from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from geopy.distance import geodesic

from ..models import DriverRequest, DocumentRequired, DocumentType, DriverDetail, User, Trip
# from ..serializers.tripSerializers import TripSerializer



class AddTripDetails(CreateAPIView):
    '''
        ADD TRIP DETAILS
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            pickup_location_lat = request.data.get('pickup_location_lat')
            pickup_location_long = request.data.get('pickup_location_long')
            drop_location_lat = request.data.get('drop_location_lat')
            drop_location_long = request.data.get('drop_location_long')

        pickup_point = (pickup_location_lat, pickup_location_long)
        droping_point = (drop_location_lat, drop_location_long)

        distance = geodesic(pickup_point, droping_point).km
        base_fair = 7
        per_km_rate_2wheeler = 10
        per_km_rate_3wheeler = 12
        per_km_rate_4wheeler = 15
        extra_at_pick_time = 2.5
        extra_at_night_time = 3
        waiting_charge = 2
        data  = {distance: distance}

        return Response(serializer.data, status=status.HTTP_201_CREATED)
