# fall_detector_console.py (через Redis)
import redis
import numpy as np
import os
import time
from datetime import datetime

fall_threshold = 1.5
PRINT_INTERVAL = 3
LOG_DIR = "/home/admin/logs"

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
last_data = {}
last_print = time.time()

def get_daily_log_file():
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(LOG_DIR, exist_ok=True)
    return os.path.join(LOG_DIR, f"falls_{today}.txt")

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def log_fall(board, ip, magnitude, gyro, accel):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gx, gy, gz = gyro
    ax, ay, az = accel
    log_line = (
        f"[{timestamp}] ❗ FALL detected!\n"
        f"    Sensor: {board} ({ip})\n"
        f"    Gyro:   x={gx:.3f}, y={gy:.3f}, z={gz:.3f}\n"
        f"    Accel:  x={ax:.3f}, y={ay:.3f}, z={az:.3f}\n"
        f"    Index:  {magnitude:.2f}\n\n"
    )

    print(log_line, end="")
    try:
        with open(get_daily_log_file(), "a") as f:
            f.write(log_line)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"⚠️ Failed to write fall log: {e}")

print("🧠 Monitoring Redis for fall events...\n")

while True:
    try:
        for i in range(1, 4):
            sensor = r.hgetall(f"sensor_{i}")
            if not sensor:
                continue

            ip = sensor.get("ip", "-")
            gx = safe_float(sensor.get("gx"))
            gy = safe_float(sensor.get("gy"))
            gz = safe_float(sensor.get("gz"))
            ax = safe_float(sensor.get("ax"))
            ay = safe_float(sensor.get("ay"))
            az = safe_float(sensor.get("az"))
            magnitude = safe_float(sensor.get("fall_index"))
            is_fall = sensor.get("fall") == "true"

            last_data[i] = {
                "ip": ip,
                "gyro": np.array([gx, gy, gz]),
                "accel": np.array([ax, ay, az]),
                "fall_index": magnitude,
                "fall": is_fall,
                "time": time.time()
            }

            if is_fall:
                log_fall(i, ip, magnitude, [gx, gy, gz], [ax, ay, az])

        if time.time() - last_print > PRINT_INTERVAL:
            print("\n========== STATUS @", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "==========")
            for i in range(1, 4):
                if i in last_data and time.time() - last_data[i]["time"] < 5:
                    d = last_data[i]
                    print(f"Sensor {i} [{d['ip']}]: ✅")
                    print(f"  Gyro: {d['gyro']}  Accel: {d['accel']}")
                    print(f"  Fall Index: {d['fall_index']:.2f}  {'❗ FALL ❗' if d['fall'] else ''}")
                else:
                    print(f"Sensor {i}: ❌ No data")
            print("============================")
            last_print = time.time()

        time.sleep(0.1)

    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(1)
