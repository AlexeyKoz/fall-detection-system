# Multi-Sensor Setup

This example demonstrates the full three-sensor configuration for maximum fall detection accuracy.

## Overview

Multi-sensor configuration provides:
- **88% detection accuracy** (validated by IEEE research)
- Fall direction determination
- Reduced false positives
- Early prediction (300-500ms before impact)
- Full body kinematics tracking

## Files in this Directory

- `console_output.txt` - Sample output showing coordinated fall detection
- `config.json` - Configuration for three-sensor setup
- `test_data.csv` - Multi-sensor test data
- `calibration_sequence.txt` - Calibration procedure for all sensors

## Configuration

### Network Setup
```json
{
  "network": {
    "ssid": "FallNet",
    "password": "1122334455",
    "raspberry_ip": "192.168.4.1",
    "udp_port": 12345
  },
  "sensors": [
    {
      "board_number": 1,
      "location": "thoracic",
      "mac_address": "AA:BB:CC:DD:EE:01",
      "position": "chest_center"
    },
    {
      "board_number": 2,
      "location": "hip",
      "mac_address": "AA:BB:CC:DD:EE:02",
      "position": "belt_center"
    },
    {
      "board_number": 3,
      "location": "knee",
      "mac_address": "AA:BB:CC:DD:EE:03",
      "position": "right_thigh"
    }
  ],
  "thresholds": {
    "fall_gyro_magnitude": 4.0,
    "warning_gyro_magnitude": 1.5,
    "multi_sensor_agreement": 2,
    "prediction_window_ms": 500
  }
}
```

## Sensor Placement Guide

### Optimal Positions
1. **Sensor 1 (Thoracic)**
   - Location: Center of chest, sternum level
   - Orientation: Y-axis pointing up, X-axis forward
   - Purpose: Upper body rotation and lean detection

2. **Sensor 2 (Hip)**
   - Location: Belt center or lower back
   - Orientation: Same as thoracic
   - Purpose: Center of mass tracking, primary fall indicator

3. **Sensor 3 (Knee/Thigh)**
   - Location: Mid-thigh, lateral side
   - Orientation: Y-axis along femur
   - Purpose: Gait analysis, trip detection

## Data Synchronization

The multi-sensor system implements:
- Time synchronization via NTP
- Quaternion-based orientation (q0, q1, q2, q3)
- 10Hz synchronized sampling
- Redis-based data aggregation

## Typical Readings During Fall Event

### Pre-Fall (T-500ms)
```
Sensor 1: Gyro: [0.5, 0.3, 0.4]  Fall Index: 0.7
Sensor 2: Gyro: [0.6, 0.4, 0.3]  Fall Index: 0.8
Sensor 3: Gyro: [0.4, 0.5, 0.6]  Fall Index: 0.9
Status: NORMAL - Slight imbalance detected
```

### Fall Initiation (T-300ms)
```
Sensor 1: Gyro: [1.2, 0.8, 1.0]  Fall Index: 1.7
Sensor 2: Gyro: [1.5, 1.0, 0.8]  Fall Index: 2.0
Sensor 3: Gyro: [1.0, 1.2, 1.4]  Fall Index: 2.1
Status: WARNING - Fall risk detected
```

### Fall Detection (T-100ms)
```
Sensor 1: Gyro: [3.4, 2.3, 4.5]  Fall Index: 6.2
Sensor 2: Gyro: [4.2, 3.1, 3.8]  Fall Index: 6.4
Sensor 3: Gyro: [2.8, 2.4, 3.5]  Fall Index: 5.1
Status: FALL DETECTED - Alert triggered
```

## Algorithm Behavior

### Multi-Sensor Voting
- Requires 2 out of 3 sensors to agree for fall confirmation
- Reduces false positives from single sensor anomalies
- Weighted voting based on sensor location

### Mathematical Model Integration
Based on Mohammed et al. (2024) IEEE paper:
```python
# Quaternion-based joint angles
thoracic_angle = calculate_angle(q_thoracic, q_reference)
hip_angle = calculate_angle(q_hip, q_reference)
knee_angle = calculate_angle(q_knee, q_reference)

# Logistic regression
p_fall = logistic_model(thoracic_angle, hip_angle, knee_angle)

# Decision threshold
if p_fall > 0.85:
    trigger_fall_alert()
```

## Testing the Demo

1. Start all system components:
```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - Receiver
python software/raspberry_pi/src/fall_receiver_redis.py

# Terminal 3 - Console Monitor
python software/raspberry_pi/src/fall_detector_console.py

# Terminal 4 - Web Interface
python software/raspberry_pi/src/fall_status_socketio.py
```

2. Simulate multi-sensor data:
```bash
# Send synchronized test data
python test/multi_sensor_simulator.py \
    --config examples/multi_sensor_setup/config.json \
    --scenario "forward_fall"
```

3. Available test scenarios:
   - `forward_fall` - Trip and fall forward
   - `backward_fall` - Slip and fall backward
   - `side_fall` - Lateral fall
   - `near_fall` - Stumble with recovery
   - `sit_to_stand` - Normal activity (no fall)
   - `walking` - Normal gait pattern

## Performance Metrics

| Metric | Single Sensor | Multi-Sensor |
|--------|--------------|--------------|
| Accuracy | 70-75% | 88% |
| Sensitivity | 65% | 71.4% |
| Specificity | 68% | 75.5% |
| False Positives | ~30% | ~12% |
| Prediction Window | None | 300-500ms |

## Calibration Procedure

### Synchronized Calibration
1. Place all sensors on a flat surface
2. Start calibration on all three simultaneously
3. Rotate all sensors together in figure-8 pattern
4. Verify all show blue LED (calibrated)
5. Test with known movements

### Individual Calibration
If sensors show different fall indices for same movement:
1. Calibrate each sensor individually
2. Use `test/calibration_check.py` to verify
3. Adjust mounting if needed

## Data Analysis

### Log File Format
```
2024-12-08 15:45:22,FALL,1,6.24,3.456,2.345,4.567,5.678,-4.345,6.234
2024-12-08 15:45:22,FALL,2,6.48,4.234,3.123,3.890,6.234,3.567,5.890
2024-12-08 15:45:22,FALL,3,5.13,2.890,2.456,3.567,4.567,-3.234,6.789
```

Fields: timestamp, event, sensor_id, fall_index, gx, gy, gz, ax, ay, az

### Visualization Tools
```python
# Plot sensor data
python tools/plot_sensor_data.py logs/falls_2024-12-08.txt

# Generate statistics
python tools/analyze_falls.py logs/
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Sensors out of sync | Network latency | Check WiFi signal strength |
| Different fall indices | Calibration mismatch | Recalibrate all sensors together |
| Missing sensor data | Connection lost | Check battery and WiFi |
| High false positives | Loose mounting | Secure sensors firmly |

## Advanced Configuration

### Custom Thresholds
Adjust for different populations:
```python
# Elderly (more sensitive)
FALL_THRESHOLD = 3.5
WARNING_THRESHOLD = 1.2

# Young adults (less sensitive)
FALL_THRESHOLD = 5.0
WARNING_THRESHOLD = 2.0
```

### Machine Learning Enhancement
The system supports ML model integration:
```python
# Load trained model
model = load_model('models/fall_predictor.h5')

# Real-time prediction
features = extract_features(sensor_data)
probability = model.predict(features)
```

## See Also
- [Single Sensor Demo](../single_sensor_demo/)
- [Main Documentation](../../README.md)
- [Research Paper](../../research/papers/IEEE_Fall_Detection_Model_2024.pdf)
- [API Reference](../../docs/API_REFERENCE.md)