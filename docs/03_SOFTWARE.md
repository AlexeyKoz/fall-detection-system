# Software Stack

## Overview

The software architecture consists of embedded firmware on ESP32 nodes and a Python-based processing system on Raspberry Pi. The system uses modern technologies for real-time data processing, storage, and visualization.

## Technology Stack

### Embedded Layer (ESP32)
- **Framework**: Arduino Core for ESP32 v2.0.11
- **Language**: C++ (Arduino-compatible)
- **Libraries**:
  - Adafruit BNO055 v1.6.0
  - Adafruit Unified Sensor v1.1.9
  - ESP32 WiFi (built-in)
  - Wire (I2C) library
  - EEPROM library

### Processing Layer (Raspberry Pi)
- **OS**: Raspberry Pi OS (64-bit)
- **Language**: Python 3.7+
- **Database**: Redis 7.0+
- **Web Framework**: Flask 2.3.2
- **WebSocket**: Flask-SocketIO 5.3.4
- **Numerical**: NumPy 1.24.3

### Network Layer
- **Access Point**: hostapd 2.9
- **DHCP Server**: dnsmasq 2.85
- **Protocol**: UDP over WiFi
- **Port**: 12345

## Software Architecture

```
┌─────────────────────────────────────────┐
│           ESP32 Firmware                │
├─────────────────────────────────────────┤
│  • Sensor Data Acquisition (I2C)        │
│  • Calibration Management (EEPROM)      │
│  • UDP Packet Transmission              │
│  • Power Management (Deep Sleep)        │
│  • LED Status Indicators                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Network Communication           │
├─────────────────────────────────────────┤
│  • WiFi Access Point (hostapd)          │
│  • DHCP Service (dnsmasq)               │
│  • UDP Protocol (Port 12345)            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Raspberry Pi Software Stack        │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │    UDP Receiver Service         │   │
│  │    (fall_receiver_redis.py)     │   │
│  └─────────────────────────────────┘   │
│              ↓                          │
│  ┌─────────────────────────────────┐   │
│  │    Redis In-Memory Database     │   │
│  │    (Message Broker & Storage)   │   │
│  └─────────────────────────────────┘   │
│              ↓                          │
│  ┌─────────────────────────────────┐   │
│  │    Processing Services          │   │
│  │  • Console Monitor              │   │
│  │  • Web Interface                │   │
│  │  • Fall Detection Algorithm     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## ESP32 Firmware Components

### Main Loop Structure
```cpp
void setup() {
    initializeHardware();
    connectWiFi();
    initializeSensor();
    loadCalibration();
}

void loop() {
    checkDeepSleepTrigger();
    handleCalibrationButton();
    readSensorData();
    transmitUDP();
    updateStatusLEDs();
}
```

### Key Functions

| Function | Purpose | Frequency |
|----------|---------|-----------|
| `readSensorData()` | Get IMU values | 10Hz |
| `transmitUDP()` | Send data packet | 10Hz |
| `handleCalibration()` | Manage calibration | On demand |
| `checkDeepSleep()` | Power management | Continuous |
| `updateLEDs()` | Status indication | Event-based |

### Configuration Parameters
```cpp
// Network Configuration
const char* ssid = "FallNet";
const char* password = "1122334455";
const char* raspberry_ip = "192.168.4.1";
const int udp_port = 12345;

// Board Identification
const int boardNumber = 1;  // Unique per sensor

// Timing Configuration
const int SEND_INTERVAL = 100;     // 10Hz
const int LOG_INTERVAL = 5000;     // 5 seconds
const int CALIB_HOLD_TIME = 3000;  // 3 seconds
```

## Raspberry Pi Software Components

### 1. UDP Receiver Service

**File**: `fall_receiver_redis.py`

```python
# Core functionality
def parse_packet(data):
    """Parse UDP packet into sensor values"""
    parts = data.decode().strip().split(",")
    return {
        'board': int(parts[0]),
        'ip': parts[1],
        'gx': float(parts[2]),
        'gy': float(parts[3]),
        'gz': float(parts[4]),
        'ax': float(parts[5]),
        'ay': float(parts[6]),
        'az': float(parts[7])
    }

def calculate_fall_index(gx, gy, gz):
    """Calculate gyroscope magnitude"""
    return np.sqrt(gx**2 + gy**2 + gz**2)
```

**Features**:
- Non-blocking UDP reception
- Data validation and sanitization
- Real-time magnitude calculation
- Redis storage with TTL

### 2. Redis Data Structure

**Schema**:
```python
# Hash structure for each sensor
sensor_1 = {
    'ip': '192.168.4.10',
    'gx': 0.123,
    'gy': -0.456,
    'gz': 0.789,
    'ax': 9.8,
    'ay': 0.1,
    'az': -0.2,
    'fall_index': 0.915,
    'fall': 'false',
    'timestamp': '2024-12-08 15:30:45'
}
```

**Commands**:
```bash
# View sensor data
redis-cli HGETALL sensor_1

# Monitor in real-time
redis-cli --scan --pattern sensor_*

# Set expiration (optional)
redis-cli EXPIRE sensor_1 60
```

### 3. Console Monitor

**File**: `fall_detector_console.py`

**Features**:
- Real-time sensor status display
- Fall event logging
- Daily log rotation
- Color-coded alerts

**Log Format**:
```
[2024-12-08 14:23:24] ◉ FALL detected!
    Sensor: 1 (192.168.4.10)
    Gyro:   x=2.345, y=1.234, z=3.456
    Accel:  x=3.456, y=-2.345, z=8.234
    Index:  4.32
```

### 4. Web Interface

**File**: `fall_status_socketio.py`

**Technologies**:
- Flask web framework
- SocketIO for WebSocket
- Real-time bidirectional communication

**Client-Side JavaScript**:
```javascript
socket.on('fall_update', function(data) {
    document.body.style.backgroundColor = 
        data.fall ? '#d62828' : '#4CAF50';
    document.body.textContent = 
        data.fall ? 'FALL' : 'STABLE';
});
```

## Configuration Files

### Network Configuration
**File**: `/etc/hostapd/hostapd.conf`
```conf
interface=wlan0
driver=nl80211
ssid=FallNet
hw_mode=g
channel=6
wmm_enabled=0
auth_algs=1
wpa=2
wpa_passphrase=1122334455
```

### DHCP Configuration
**File**: `/etc/dnsmasq.conf`
```conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

### Python Dependencies
**File**: `requirements.txt`
```
redis==4.5.1
flask==2.3.2
flask-socketio==5.3.4
numpy==1.24.3
python-socketio==5.9.0
```

## Service Management

### Systemd Services

**UDP Receiver Service**:
```ini
[Unit]
Description=Fall Detection UDP Receiver
After=network.target redis.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin
Environment="PATH=/home/admin/venv/bin"
ExecStart=/home/admin/venv/bin/python /home/admin/fall_receiver_redis.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Auto-Start Script
**File**: `autostart_fall_system.sh`
```bash
#!/bin/bash
# Start Redis
redis-server --daemonize yes

# Activate virtual environment
source /home/admin/venv/bin/activate

# Start services
nohup python fall_receiver_redis.py &
nohup python fall_detector_console.py &
nohup python fall_status_socketio.py &

# Launch browser in kiosk mode
chromium-browser --kiosk http://localhost:5000 &
```

## Development Environment

### Required Tools
- **Arduino IDE**: 1.8.19+ or 2.x
- **Python**: 3.7+
- **Git**: Version control
- **VS Code**: Recommended editor

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## API Endpoints

### UDP Data Format
```
Endpoint: UDP 192.168.4.1:12345
Format: CSV
Fields: board_id,ip,gx,gy,gz,ax,ay,az
Rate: 10Hz per sensor
```

### WebSocket Events
```
Event: 'fall_update'
Data: {
    'fall': boolean,
    'sensors': array,
    'timestamp': string
}
```

### Redis Commands
```python
# Python API
r = redis.Redis(host='localhost', port=6379)
r.hset('sensor_1', mapping=data)
sensor_data = r.hgetall('sensor_1')
```

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ConnectionRefusedError` | Redis not running | Start Redis service |
| `OSError: Address in use` | Port already used | Kill existing process |
| `ImportError` | Missing library | Install dependencies |
| `UnicodeDecodeError` | Invalid packet | Add try-except block |

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/admin/logs/system.log'),
        logging.StreamHandler()
    ]
)
```

## Testing

### Unit Tests
```python
# test_packet_parser.py
def test_parse_valid_packet():
    data = b"1,192.168.4.10,0.1,-0.2,0.3,9.8,0.1,-0.1"
    result = parse_packet(data)
    assert result['board'] == 1
    assert result['gx'] == 0.1
```

### Integration Tests
```bash
# Send test UDP packet
echo "1,192.168.4.10,0.1,-0.2,0.3,9.8,0.1,-0.1" | \
    nc -u 192.168.4.1 12345

# Check Redis
redis-cli HGETALL sensor_1
```

---
*Next: [Fall Detection Algorithms](04_ALGORITHMS.md)*