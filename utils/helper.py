import requests

def calculate_road_distance_and_time(start_lat, start_lon, end_lat, end_lon, api_key):
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    body = {
        "coordinates": [
            [start_lon, start_lat],   # longitude first, then latitude
            [end_lon, end_lat]
        ]
    }

    response = requests.post(
        'https://api.openrouteservice.org/v2/directions/driving-car',
        headers=headers,
        json=body
    )

    data = response.json()
    # print(data,"----------")
    distance_in_meters = data['routes'][0]['summary']['distance']
    duration_in_seconds = data['routes'][0]['summary']['duration']

    distance_in_km = round(distance_in_meters / 1000, 2)
    duration_in_minutes = round(duration_in_seconds / 60, 1)

    return distance_in_km, duration_in_minutes