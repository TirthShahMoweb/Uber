from django.urls import path
from .consumers import TripUpdateConsumer

websocket_urlpatterns = [
    path("ws/trip_updates/", TripUpdateConsumer.as_asgi()),  # Make sure this matches EXACTLY
]