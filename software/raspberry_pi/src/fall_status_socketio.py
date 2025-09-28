# fall_status_socketio.py
from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO
import redis
import time
import threading

# === Flask & Redis Configuration ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# === HTML template with WebSocket client ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Fall Detection</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            font-size: 8vw;
            text-transform: uppercase;
            transition: background-color 0.2s, color 0.2s;
            background-color: #4CAF50;
            color: #f0f0f0;
        }
    </style>
    <script src=\"/socket.io.min.js\"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const socket = io();
            console.log("WebSocket connected");

            socket.on('connect', () => {
                console.log("✅ Connected to WebSocket server");
            });

            socket.on('fall_update', function (data) {
                console.log("📡 Received:", data);
                document.body.style.backgroundColor = data.fall ? '#d62828' : '#4CAF50';
                document.body.textContent = data.fall ? 'FALL' : 'STABLE';
                document.body.style.color = data.fall ? '#ffffff' : '#f0f0f0';
            });

            socket.on('disconnect', () => {
                console.warn("❌ Disconnected from WebSocket server");
            });
        });
    </script>
</head>
<body>
    STABLE
</body>
</html>
"""

# Serve main page
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# Serve static Socket.IO client file
@app.route("/socket.io.min.js")
def serve_socketio():
    print("📦 Serving socket.io.min.js!")
    return send_from_directory("/home/admin", "socket.io.min.js")

# Background thread that polls Redis for sensor fall status

def redis_monitor():
    print("🧠 Redis monitor thread started")
    last_state = None  # To avoid duplicate emission
    try:
        while True:
            fall_detected = False
            for i in range(1, 4):  # Iterate over sensor_1 to sensor_3
                try:
                    sensor = r.hgetall(f"sensor_{i}")  # Read all fields from sensor_i
                    if sensor.get("fall") == "true":  # If any sensor reports a fall, mark fall_detected
                        fall_detected = True
                        break
                except Exception as e:
                    print(f"⚠️ Redis read error: {e}")
                    continue

            # Only emit if the state has changed
            if fall_detected != last_state:
                socketio.emit('fall_update', {'fall': fall_detected})
                print(f"[SOCKETIO] Emitted: {'FALL' if fall_detected else 'STABLE'}")
                last_state = fall_detected

            time.sleep(0.1)  # Polling interval
    except Exception as e:
        print(f"❌ Background task crashed: {e}")

# Start Flask app with background thread
if __name__ == '__main__':
    print("🧠 Starting SocketIO with background Redis monitor...")
    socketio.start_background_task(redis_monitor)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
