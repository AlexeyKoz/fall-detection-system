# System Architecture

## Overview

The Fall Detection System employs a distributed architecture designed for real-time processing, scalability, and reliability. The system consists of wireless sensor nodes that communicate with a central processing unit, implementing a multi-layered approach for data collection, processing, and alerting.

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Sensor Node 1 │     │   Sensor Node 2 │     │   Sensor Node 3 │
│   (Thoracic)    │     │      (Hip)      │     │     (Knee)      │
│                 │     │                 │     │                 │
│  ESP32 + BNO055 │     │  ESP32 + BNO055 │     │  ESP32 + BNO055 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │      UDP/WiFi         │      UDP/WiFi         │      UDP/WiFi
         │      10Hz             │      10Hz             │      10Hz
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     WiFi Access Point   │
                    │    (FallNet Network)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Raspberry Pi 5      │
                    │   Central Processing    │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐    ┌─────────▼─────────┐   ┌─────────▼────────┐
│  UDP Receiver  │    │  Redis Data Store  │   │  Web Interface   │
│  (Port 12345)  │    │   (In-Memory DB)   │   │   (Port 5000)    │
└────────────────┘    └───────────────────┘   └──────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Fall Detection Logic  │
                    │  - Threshold Detection  │
                    │  - Quaternion Analysis  │
                    │  - Logistic Regression  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Alert System        │
                    │  - Console Logging      │
                    │  - Web Socket Updates   │
                    │  - Future: SMS/Email    │
                    └─────────────────────────┘
```

## Component Layers

### 1. Sensor Layer
- **Components**: 3× ESP32 with BNO055 sensors
- **Function**: Data acquisition and transmission
- **Protocol**: UDP over WiFi
- **Data Rate**: 10 Hz per sensor

### 2. Network Layer
- **Technology**: WiFi 802.11n (2.4GHz)
- **Topology**: Star network with RPi as access point
- **SSID**: FallNet
- **Security**: WPA2 encryption

### 3. Processing Layer
- **Platform**: Raspberry Pi 5
- **Components**:
  - UDP Receiver (Python)
  - Redis (Message broker)
  - Algorithm Engine
  - WebSocket Server

### 4. Application Layer
- **Console Monitor**: Terminal-based monitoring
- **Web Interface**: Real-time browser display
- **Logging System**: Daily rotating logs
- **Alert System**: Visual and future audio alerts

## Data Flow Architecture

### 1. Data Acquisition Path
```
BNO055 Sensor
    ↓ (I2C @ 400kHz)
ESP32 Microcontroller
    ↓ (Processing & Packaging)
UDP Packet Formation
    ↓ (WiFi @ 10Hz)
Network Transmission
```

### 2. Data Processing Pipeline
```
UDP Reception → Parse → Validate → Calculate → Store → Analyze → Alert
     ↓            ↓         ↓          ↓        ↓        ↓        ↓
Port 12345    Extract   Check     Magnitude  Redis   Threshold  Trigger
              Values    Ranges    & Indices   Hash    Compare
```

### 3. Data Storage Schema
```
Redis Hash Structure:
sensor_1 {
    ip: "192.168.4.10"
    gx, gy, gz: gyroscope values
    ax, ay, az: accelerometer values
    fall_index: calculated magnitude
    fall: boolean status
    timestamp: last update
}
```

## Communication Protocols

### UDP Packet Format
```
Structure: "board_id,ip,gx,gy,gz,ax,ay,az"
Example:   "2,192.168.4.11,0.123,-0.456,0.789,9.8,0.1,-0.2"
Size:      ~80 bytes per packet
Frequency: 10 packets/second per sensor
```

### WebSocket Events
```javascript
// Server → Client
socket.emit('fall_update', {
    fall: true/false,
    sensors: [...]
});

// Client → Server  
socket.on('connect', callback);
socket.on('disconnect', callback);
```

## System Boundaries

### Physical Boundaries
- **Range**: 30m indoor / 100m outdoor
- **Sensors**: Maximum 127 (I2C limit)
- **Concurrent Users**: Up to 100 per network

### Performance Boundaries
- **Latency**: <100ms end-to-end
- **Throughput**: 30 packets/second nominal
- **Storage**: 24 hours of logs (~100MB)

## Scalability Considerations

### Horizontal Scaling
- Multiple Raspberry Pi units for different areas
- MQTT broker for inter-Pi communication
- Cloud aggregation for multi-site deployment

### Vertical Scaling
- Raspberry Pi cluster for increased processing
- GPU acceleration for ML models
- Dedicated database server for long-term storage

## Security Architecture

### Network Security
- WPA2 encryption for WiFi
- Static IP assignments
- Isolated network (no internet required)
- MAC address filtering (optional)

### Data Security
- Redis bound to localhost only
- No sensitive data transmission
- Anonymized sensor IDs
- Local-only processing

## Fault Tolerance

### Sensor Failure Handling
- Continues operation with 2/3 sensors
- Alerts on sensor disconnection
- Automatic reconnection attempts
- EEPROM calibration persistence

### Network Failure Recovery
- UDP fire-and-forget (no blocking)
- Sensor buffering during disconnection
- Automatic WiFi reconnection
- Independent sensor operation

### Processing Failure Mitigation
- Service auto-restart scripts
- Watchdog timer implementation
- Redis persistence options
- Redundant logging paths

## Future Architecture Enhancements

### Planned Improvements
1. **Edge Computing**: On-sensor fall detection
2. **Mesh Networking**: Sensor-to-sensor communication
3. **Cloud Integration**: Remote monitoring dashboard
4. **Machine Learning**: Adaptive thresholds
5. **Multi-Modal Sensing**: Heart rate, SpO2 integration

### Architecture Evolution Path
```
Phase 1 (Current): Local processing, WiFi communication
Phase 2: Edge computing, mesh network
Phase 3: Cloud integration, ML models
Phase 4: Predictive analytics, preventive alerts
```

---
*Next: [Hardware Components](02_HARDWARE.md)*