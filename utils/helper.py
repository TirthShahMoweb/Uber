import requests

def calculate_road_distance_and_time(start_lat, start_lon, end_lat, end_lon, api_key):
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    body = {
        "coordinates": [
            [float(start_lon), float(start_lat)],
            [float(end_lon), float(end_lat)]
        ]
    }

    response = requests.post(
        'https://api.openrouteservice.org/v2/directions/driving-car',
        headers=headers,
        json=body
    )
    if response.status_code != 200:
        print(f"[ERROR] Status code: {response.status_code}")
        print(f"[ERROR] Response text: {response.text}")
        raise Exception("OpenRouteService API error")

    try:
        data = response.json()
    except Exception as e:
        print("[ERROR] Failed to parse JSON:", e)
        print("Response text:", response.text)
        raise

    distance_in_meters = data['routes'][0]['summary']['distance']
    duration_in_seconds = data['routes'][0]['summary']['duration']

    distance_in_km = round(distance_in_meters / 1000, 2)
    duration_in_minutes = round(duration_in_seconds / 60, 1)

    return distance_in_km, duration_in_minutes
