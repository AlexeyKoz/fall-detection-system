# Fall_Reciver_Redis.py
import socket
import redis
import numpy as np
import math
from datetime import datetime

# === Configuration ===
UDP_IP = "0.0.0.0"  # Listen on all network interfaces
UDP_PORT = 12345     # UDP port to listen on
BUFFER_SIZE = 2048   # Maximum size of incoming UDP packets
fall_threshold = 1000  # Threshold for gyro magnitude to detect fall (to be tuned)

# Connect to Redis server
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("✅ Listening for fall data on UDP port", UDP_PORT)

# Create and bind UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.5)  # Timeout for receiving data to avoid blocking

# Function to parse incoming UDP data packet
def parse_packet(data):
    try:
        parts = data.decode().strip().split(",")
        board = int(parts[0])            # Sensor board ID
        ip = parts[1]                    # IP address of sender
        gx, gy, gz = float(parts[2]), float(parts[3]), float(parts[4])  # Gyroscope x, y, z
        ax, ay, az = float(parts[5]), float(parts[6]), float(parts[7])  # Accelerometer x, y, z
        return board, ip, gx, gy, gz, ax, ay, az
    except Exception as e:
        print("❌ Parse error:", e)
        return None, None, None, None, None, None, None, None

# === Main loop to process data ===
while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)  # Receive UDP packet
        board, ip, gx, gy, gz, ax, ay, az = parse_packet(data)
        if board is None:
            continue

        # Skip invalid or NaN values
        if any(map(lambda v: v is None or math.isnan(v), [gx, gy, gz, ax, ay, az])):
            print(f"⚠️ Skipped sensor {board}: invalid data")
            continue

        # Calculate vector magnitudes
        gyro_vector = np.array([gx, gy, gz])
        accel_vector = np.array([ax, ay, az])

        gyro_magnitude = float(np.linalg.norm(gyro_vector))  # Total angular velocity
        accel_magnitude = float(np.linalg.norm(accel_vector))  # Total linear acceleration

        # Determine fall based on gyro threshold only (for now)
        is_fall = gyro_magnitude > fall_threshold

        # Print data to console for debugging
        print(f"[Sensor {board}] Gyro: ({gx:.2f}, {gy:.2f}, {gz:.2f})  Accel: ({ax:.2f}, {ay:.2f}, {az:.2f}) → Index: {gyro_magnitude:.2f} → Fall: {is_fall}")

        # Store data in Redis with key per board
        r.hset(f"sensor_{board}", mapping={
            "ip": ip,
            "gx": round(gx, 3),
            "gy": round(gy, 3),
            "gz": round(gz, 3),
            "ax": round(ax, 3),
            "ay": round(ay, 3),
            "az": round(az, 3),
            "fall_index": round(gyro_magnitude, 3),
            "accel_index": round(accel_magnitude, 3),
            "fall": "true" if is_fall else "false",
            "timestamp": str(datetime.now())
        })

    except socket.timeout:
        continue  # Loop again if no data received
    except Exception as e:
        print("⚠️ Error:", e)
