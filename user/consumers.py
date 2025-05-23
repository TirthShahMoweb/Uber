import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TripUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from rest_framework_simplejwt.tokens import AccessToken

        from user.models import User

        query_string = self.scope['query_string'].decode()  # Decode the query string
        token = None

        if 'token=' in query_string:
            token = query_string.split('token=')[1]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)  # Get the user asynchronously

                if user is not None and isinstance(user, User):
                    self.user = user
                    self.group_name = f'driver_{user.id}'
                    await self.channel_layer.group_add(self.group_name, self.channel_name)
                    await self.accept()
                else:
                    await self.close()
            except Exception as e:
                await self.close()
        else:
            await self.close()


    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # print(text_data,"-==-=-=-=-")
        data = json.loads(text_data)
        event_type = data.get("type")
        location = data.get("location")
        if event_type == "receive_location_update":
            # {"type": "receive_location_update", "location":"pickup_location", "status":"success", "data" : {"trip_id": 232, "lat": '23.055770872666034', "long": '72.54309146797485'}}
            payload = data.get("data", {})
            trip_id = payload.get("trip_id")
            latitude = payload.get("lat")
            longitude = payload.get("long")


            from asgiref.sync import sync_to_async

            from user.models import Trip, TripLocation

            from .serializers.tripSerializers import \
                DriverPersonalInfoSerializer
            trip = await Trip.objects.select_related("customer", "driver").aget(id=trip_id)
            await sync_to_async(TripLocation.objects.create)(
                trip_id=trip_id, latitude=latitude, longitude=longitude
            )
            customer_id = trip.customer.id
            driver_id = trip.driver.id

            import math
            from datetime import timedelta

            import pytz
            from django.utils import timezone

            from Uber.settings import open_route_service_key
            from utils.helper import calculate_road_distance_and_time
            from vehicle.models import Vehicle

            india_timezone = pytz.timezone('Asia/Kolkata')
            current_time_utc = timezone.now()
            current_time_ist = current_time_utc.astimezone(india_timezone)
            distance, durations = 0, 0

            if location == "pickup_location":
                distance, durations = calculate_road_distance_and_time(trip.pickup_location_latitude, trip.pickup_location_longitude, latitude, longitude, open_route_service_key)
            elif location == "drop_location":
                distance, durations = calculate_road_distance_and_time(latitude, longitude, trip.drop_location_latitude, trip.drop_location_longitude, open_route_service_key)

            distance = float(distance)
            data  = {'id' : trip.id,
                    'pickup_location': trip.pickup_location,
                    'drop_location': trip.drop_location,
                    "distance": 0,
                    'total_fare': float(trip.fare),
                    'name': f"{trip.customer.first_name} {trip.customer.last_name}",
                    'estimated_time': f'{math.ceil(durations)} mins',
                    'durations': (current_time_ist + timedelta(minutes=math.ceil(durations))).strftime("%I:%M %p"),
                    'mobile_number': trip.customer.mobile_number
                    }

            request_context = {"server": self.scope['server']}
            serializer = DriverPersonalInfoSerializer(trip.driver, context=request_context)

            # Driver data
            await self.channel_layer.group_send(
                f"driver_{driver_id}",
                {
                    "type": "location_update",
                    "message": {
                        'status': 'success',
                        'message': 'Location Updated Successfully',
                        'event': 'location_update',
                        'data': data
                    }
                }
            )
            vehicle_id = await sync_to_async(lambda: trip.vehicle_id)()
            vehicle = await Vehicle.objects.filter(id=trip.vehicle_id.id).afirst()
            data['otp']= trip.otp
            data['name']= f"{trip.driver.first_name} {trip.driver.last_name}"
            data['image']= serializer.data['thumbnail_pic']
            data['mobile_number']= serializer.data['mobile_number']
            data['vehicle_number']= vehicle.vehicle_number

            # Customer Data
            await self.channel_layer.group_send(
                f"driver_{customer_id}",
                {
                    "type": "location_update",
                    "message": {
                        'status': 'success',
                        'message': 'Location Updated Successfully',
                        'event': 'location_update',
                        'data': data
                    }
                }
            )

    async def send_trip_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))


    async def remove_trip_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))



    @staticmethod
    async def get_user(user_id):
        from django.contrib.auth.models import AnonymousUser

        from user.models import User

        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
