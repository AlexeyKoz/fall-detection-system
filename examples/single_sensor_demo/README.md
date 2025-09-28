# Single Sensor Demo

This example demonstrates a minimal fall detection setup using only one sensor node.

## Overview

Single sensor configuration is suitable for:
- Basic fall detection
- Testing and development
- Budget-constrained deployments
- Monitoring seated or bed-bound individuals

## Files in this Directory

- `console_output.txt` - Sample console output showing fall detection
- `config.json` - Configuration for single sensor setup
- `test_data.csv` - Sample sensor data for testing

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
      "location": "chest",
      "mac_address": "AA:BB:CC:DD:EE:01"
    }
  ],
  "thresholds": {
    "fall_gyro_magnitude": 4.0,
    "warning_gyro_magnitude": 1.5
  }
}
```

## Sample Data Format

The sensor transmits data in CSV format:
```
board_number,ip_address,gyro_x,gyro_y,gyro_z,accel_x,accel_y,accel_z
1,192.168.4.10,0.123,-0.045,0.089,0.982,-0.145,9.798
```

## Typical Sensor Readings

### Normal Activity
- **Gyro magnitude**: 0.1 - 0.5 rad/s
- **Accel magnitude**: ~9.8 m/s² (gravity)
- **Fall index**: < 1.0

### Walking
- **Gyro magnitude**: 0.5 - 1.5 rad/s
- **Accel magnitude**: 9.0 - 11.0 m/s²
- **Fall index**: 0.5 - 1.5

### Fall Event
- **Gyro magnitude**: > 4.0 rad/s
- **Accel magnitude**: Variable (3.0 - 15.0 m/s²)
- **Fall index**: > 4.0

## Testing the Demo

1. Start the Raspberry Pi system:
```bash
cd software/raspberry_pi
python src/fall_receiver_redis.py &
python src/fall_detector_console.py
```

2. Simulate sensor data:
```bash
# Send test UDP packets
python test/send_test_data.py --file examples/single_sensor_demo/test_data.csv
```

3. Monitor console output for fall detection

## Limitations

Single sensor configuration has limitations:
- Lower accuracy (70-75%)
- Cannot distinguish fall direction
- May miss falls if sensor is on unaffected body part
- Higher false positive rate

## Recommended Placement

For single sensor deployment, optimal placement is:
- **Primary**: Chest/sternum (captures upper body movement)
- **Alternative**: Waist/belt (near center of mass)

## Upgrading to Multi-Sensor

To improve accuracy, consider upgrading to the [multi-sensor setup](../multi_sensor_setup/).

## See Also
- [Multi-Sensor Setup](../multi_sensor_setup/)
- [Main Documentation](../../README.md)
- [Hardware Setup Guide](../../docs/HARDWARE_SETUP.md)