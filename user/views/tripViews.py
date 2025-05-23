from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
import pytz
from decimal import Decimal
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from datetime import time
from datetime import timedelta
import math
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import DriverRequest, DocumentRequired, DocumentType, DriverDetail, User, Trip, TripFare
from ..serializers.tripSerializers import TripSerializer
from utils.helper import calculate_road_distance_and_time
from Uber.settings import open_route_service_key



# class TripDetails(ListAPIView):
#     '''
#         TRIP DETAILS
#     '''
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = TripSerializer

#     def list(self, request, *args, **kwargs):
#         user = request.user
#         india_timezone = pytz.timezone('Asia/Kolkata')
#         current_time_utc = timezone.now()
#         current_time_ist = current_time_utc.astimezone(india_timezone)
#         current_time_only = current_time_ist.time()

#         serializer = self.get_serializer(data=request.data,context={'user':user})
#         if serializer.is_valid():
#             pickup_location_long = request.data.get('pickup_location_longitude')
#             pickup_location_lat = request.data.get('pickup_location_latitude')
#             drop_location_lat = request.data.get('drop_location_latitude')
#             drop_location_long = request.data.get('drop_location_longitude')
#             distance, durations = calculate_road_distance_and_time(pickup_location_lat, pickup_location_long, drop_location_lat, drop_location_long, open_route_service_key)
#             base_fair = 5
#             per_km_rate_2wheeler = 7
#             per_km_rate_3wheeler = 10
#             per_km_rate_4wheeler = 15
#             extra_at_pick_time = 2.5
#             extra_at_night_time = 3
#             total_fare = {}
#             if current_time_only >= time(22, 30) or current_time_only < time(7, 0):
#                 total_fare['2 wheeler'] = base_fair + (per_km_rate_2wheeler + extra_at_night_time) * distance
#                 total_fare['3 wheeler'] = base_fair + (per_km_rate_3wheeler + extra_at_night_time) * distance
#                 total_fare['4 wheeler'] = base_fair + (per_km_rate_4wheeler + extra_at_night_time) * distance
#                 print("Apply night fare")

#             elif time(9, 0) <= current_time_only <= time(11, 0) or time(18, 0) <= current_time_only <= time(20, 0):
#                 total_fare['2 wheeler'] = base_fair + (per_km_rate_2wheeler + extra_at_pick_time) * distance
#                 total_fare['3 wheeler'] = base_fair + (per_km_rate_3wheeler + extra_at_pick_time) * distance
#                 total_fare['4 wheeler'] = base_fair + (per_km_rate_4wheeler + extra_at_pick_time) * distance
#                 print("Apply peak fare")

#             else:
#                 total_fare['2 wheeler'] = base_fair + (per_km_rate_2wheeler * distance)
#                 total_fare['3 wheeler'] = base_fair + (per_km_rate_3wheeler * distance)
#                 total_fare['4 wheeler'] = base_fair + (per_km_rate_4wheeler * distance)
#                 print("Apply normal fare")

#             data  = {"distance": f"{distance} km",
#                      'durations': (current_time_ist + timedelta(minutes=math.ceil(durations))).strftime("%I:%M %p"),
#                      'pickup_location': serializer.data['pickup_location'],
#                      'drop_location': serializer.data['drop_location'],
#                      'total_fare':total_fare}

#             return Response({"status":"success","message":"Successfully","data":data}, status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class TripDetails(CreateAPIView):
    '''
        TRIP DETAILS
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        india_timezone = pytz.timezone('Asia/Kolkata')
        current_time_utc = timezone.now()
        current_time_ist = current_time_utc.astimezone(india_timezone)
        current_time_only = current_time_ist.time()

        pickup_location_long = request.data.get('pickup_location_longitude')
        pickup_location_lat = request.data.get('pickup_location_latitude')
        drop_location_lat = request.data.get('drop_location_latitude')
        drop_location_long = request.data.get('drop_location_longitude')
        if not pickup_location_lat:
            return Response({"status":"success","message":"Successfully","data":{}}, status=status.HTTP_200_OK)

        if not pickup_location_long:
            return Response({"status":"success","message":"Successfully","data":{}}, status=status.HTTP_200_OK)

        if not drop_location_lat:
            return Response({"status":"success","message":"Successfully","data":{}}, status=status.HTTP_200_OK)

        if not drop_location_long:
            return Response({"status":"success","message":"Successfully","data":{}}, status=status.HTTP_200_OK)

        distance, durations = calculate_road_distance_and_time(pickup_location_lat, pickup_location_long, drop_location_lat, drop_location_long, open_route_service_key)
        distance = Decimal(str(distance))
        base_fair = 5
        total_fare = {}
        fares = TripFare.objects.all()

        for fare in fares:
            if current_time_only >= fare.night_time_starting or current_time_only < fare.night_time_ending:
                total_fare[fare.vehicle_type] = base_fair + (fare.normal_fare + fare.night_time_fare ) * distance

            elif fare.peak_time_morning_starting <= current_time_only <= fare.peak_time_morning_ending or fare.peak_time_evening_starting <= current_time_only <= fare.peak_time_evening_starting:
                total_fare[fare.vehicle_type] = base_fair + (fare.normal_fare + fare.peak_time_fare ) * distance

            else:
                total_fare[fare.vehicle_type] = base_fair + (fare.normal_fare * distance)

        data  = {"distance": f"{distance} km",
                    'durations': (current_time_ist + timedelta(minutes=math.ceil(durations))).strftime("%I:%M %p"),
                    'estimated_time': f'{math.ceil(durations)} mins',
                    'pickup_location': request.data['pickup_location'],
                    'drop_location': request.data['drop_location'],
                    'total_fare':total_fare}

        return Response({"status":"success","message":"Successfully","data":data}, status=status.HTTP_200_OK)


class AddTripDetails(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            trip = serializer.save()
            print(user)
            user = get_object_or_404(User, mobile_number=user)
            data = {
                "id": trip.id,
                "distance": f"{trip.distance} km",
                "pickup_location": trip.pickup_location,
                "drop_location": trip.drop_location,
                "vehicle_type": trip.vehicle_type,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "fare": f"Rs. {trip.fare}"
            }

            vehicle_type = trip.vehicle_type
            drivers = DriverDetail.objects.filter(in_use__vehicle_type=vehicle_type)
            channel_layer = get_channel_layer()

            for driver in drivers:
                group_name = f'driver_{driver.user.id}'
                print(f"📢 Sending WebSocket update to group: {group_name}")  # Debugging

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'send_trip_update',
                        'message': {
                            'status': 'New trip available',
                            'data': data
                        }
                    }
                )
            return Response({"status": "success", "message": "Successfully added trip", "data": data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)