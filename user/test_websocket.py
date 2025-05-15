import websocket
import threading
import time

# Replace with your actual token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3Mzc2MDI1LCJpYXQiOjE3NDcyMDMyMjUsImp0aSI6IjEyZTk3Y2E3ODMwMTQ4ZDhiNTNkYzU5NTU0YjZiNDQ0IiwidXNlcl9pZCI6NH0.H_AoZgxr7b7rVbW3Ap5eOWyhfM7o9pmx9wzvKj4RZiY"

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")

def on_open(ws):
    print("🔗 WebSocket Connected!")
    # Optionally send a message
    ws.send("Hello from client")

# Construct WebSocket URL
ws_url = f"ws://192.168.50.7:8000/ws/trip_updates/?token={TOKEN}"

# Use WebSocketApp
ws_app = websocket.WebSocketApp(ws_url,
                                 on_open=on_open,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)

# Run in a thread
thread = threading.Thread(target=ws_app.run_forever)
thread.start()
