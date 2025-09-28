# Deployment Guide

## Pre-Deployment Checklist

### Hardware Verification

- [ ] All ESP32 boards tested individually
- [ ] BNO055 sensors responding on I2C
- [ ] Batteries charged to 100%
- [ ] LEDs and buttons functioning
- [ ] WiFi range tested in deployment area
- [ ] Raspberry Pi cooling adequate

### Software Verification

- [ ] Latest firmware on all ESP32 nodes
- [ ] Raspberry Pi OS updated
- [ ] All Python services running
- [ ] Redis operational
- [ ] Web interface accessible
- [ ] Logs rotating properly

### Network Verification

- [ ] WiFi access point active
- [ ] DHCP serving addresses
- [ ] All sensors connecting
- [ ] UDP packets received
- [ ] No IP conflicts

## Step-by-Step Deployment

### Phase 1: Infrastructure Setup

#### 1.1 Raspberry Pi Preparation

```bash
# Clone repository
git clone https://github.com/AlexeyKoz/fall-detection-system.git
cd fall-detection-system

# Run setup script
sudo bash software/raspberry_pi/scripts/setup_fallnet.sh

# Verify services
systemctl status hostapd dnsmasq
```

#### 1.2 Network Testing

```bash
# Check access point
sudo hostapd_cli status

# Verify IP configuration
ip addr show wlan0

# Test UDP reception
nc -ul 12345
```

### Phase 2: Sensor Node Deployment

#### 2.1 Firmware Upload

For each ESP32 node:

1. **Configure Board Number**:
```cpp
const int boardNumber = 1;  // Change for each sensor (1, 2, or 3)
```

2. **Upload Firmware**:
```bash
# Using Arduino IDE
# Select: Tools → Board → ESP32 Dev Module
# Select: Tools → Port → [Your COM port]
# Click: Upload
```

3. **Verify Connection**:
```bash
# Monitor serial output
# Should see: "✅ Wi-Fi Connected!"
```

#### 2.2 Initial Calibration

For each sensor:

1. Power on the sensor
2. Wait for WiFi connection (Status LED on)
3. Hold calibration button for 3 seconds
4. Yellow LED starts blinking
5. Rotate sensor in figure-8 pattern
6. Blue LED indicates completion
7. Verify calibration saved

### Phase 3: System Integration

#### 3.1 Start All Services

```bash
# On Raspberry Pi
sudo systemctl start fall-receiver
sudo systemctl start fall-console
sudo systemctl start fall-web

# Verify all running
sudo systemctl status fall-receiver fall-console fall-web
```

#### 3.2 Verify Data Flow

```bash
# Monitor UDP packets
sudo tcpdump -i wlan0 -n udp port 12345

# Check Redis data
redis-cli
> HGETALL sensor_1
> HGETALL sensor_2
> HGETALL sensor_3

# View console output
sudo journalctl -f -u fall-console
```

#### 3.3 Web Interface Check

```bash
# Open browser
chromium-browser http://localhost:5000

# Or remotely
http://192.168.4.1:5000
```

### Phase 4: Physical Installation

#### 4.1 Sensor Placement

**Optimal Positions**:

| Sensor # | Location | Attachment Method | Orientation |
|----------|----------|-------------------|-------------|
| 1 | Chest/Sternum | Elastic strap or vest pocket | Y-axis vertical, X-axis forward |
| 2 | Hip/Waist | Belt clip or waistband | Same as chest |
| 3 | Thigh | Elastic band or pocket | Y-axis along femur |

**Mounting Guidelines**:
- Secure firmly to minimize movement
- Ensure comfort for extended wear
- Verify LED visibility for status
- Keep buttons accessible

#### 4.2 Final Calibration

After mounting on person:

1. Person stands in T-pose
2. Recalibrate all sensors
3. Verify similar readings when stationary
4. Test with controlled movements
5. Adjust thresholds if needed

### Phase 5: Validation Testing

#### 5.1 Functional Tests

**Test Sequence**:

1. **Stationary Test** (2 minutes)
   - Person stands still
   - Verify no false positives
   - Check baseline readings

2. **Walking Test** (5 minutes)
   - Normal walking pace
   - Monitor fall indices
   - Should remain < 1.5

3. **Daily Activities** (10 minutes)
   - Sitting/standing
   - Reaching
   - Turning
   - Verify no false alarms

4. **Controlled Fall** (with safety mats)
   - Simulate forward fall
   - Verify detection < 100ms
   - Check all sensors trigger

#### 5.2 Performance Validation

```python
# Run validation script
python tests/validate_deployment.py

Expected Output:
✓ All sensors connected
✓ Latency < 100ms
✓ Packet loss < 1%
✓ Redis operational
✓ Web interface responsive
✓ Logging functional
```

## Production Configuration

### Environment-Specific Settings

#### Home Environment
```python
# config/home_config.py
FALL_THRESHOLD = 3.5  # More sensitive
WARNING_THRESHOLD = 1.2
ALERT_DELAY = 10  # seconds before alert
ENABLE_AUDIO = True
```

#### Clinical Environment
```python
# config/clinical_config.py
FALL_THRESHOLD = 4.0  # Balanced
WARNING_THRESHOLD = 1.5
ALERT_DELAY = 5
ENABLE_LOGGING = True
ENABLE_CLOUD_BACKUP = True
```

#### Research Environment
```python
# config/research_config.py
FALL_THRESHOLD = 4.5  # Less sensitive
WARNING_THRESHOLD = 2.0
SAVE_RAW_DATA = True
ENABLE_DEBUG = True
```

### Security Hardening

#### 1. Network Security

```bash
# Change default password
sudo nano /etc/hostapd/hostapd.conf
# wpa_passphrase=YOUR_STRONG_PASSWORD

# Enable MAC filtering (optional)
# macaddr_acl=1
# accept_mac_file=/etc/hostapd/accept.mac

# Firewall rules
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 5000/tcp  # Web interface
sudo ufw allow 12345/udp  # Sensor data
```

#### 2. System Security

```bash
# Change default user password
passwd

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Regular updates
sudo apt update && sudo apt upgrade -y
```

## Maintenance Procedures

### Daily Maintenance

- [ ] Check battery levels
- [ ] Verify all sensors connected
- [ ] Review fall event logs
- [ ] Clear old log files if needed

### Weekly Maintenance

- [ ] Test calibration status
- [ ] Clean sensor contacts
- [ ] Check mounting straps
- [ ] Backup configuration

### Monthly Maintenance

- [ ] Full system reboot
- [ ] Update software if available
- [ ] Review performance metrics
- [ ] Replace batteries if < 80% capacity

## Troubleshooting Deployment Issues

### Common Problems and Solutions

#### Sensor Not Connecting

```bash
# Diagnosis
1. Check WiFi credentials in firmware
2. Verify access point running
3. Check DHCP pool not exhausted
4. Monitor serial output for errors

# Solution
- Reflash firmware with correct settings
- Restart hostapd service
- Expand DHCP range
```

#### High False Positive Rate

```bash
# Diagnosis
1. Check sensor mounting (loose?)
2. Verify calibration current
3. Review threshold settings
4. Analyze activity patterns

# Solution
- Secure sensors properly
- Recalibrate all sensors
- Adjust thresholds:
  redis-cli SET fall_threshold 5.0
```

#### Missing Data Packets

```bash
# Diagnosis
sudo tcpdump -i wlan0 -n udp port 12345 -c 100
# Check packet rate (should be ~10Hz per sensor)

# Solution
- Check WiFi signal strength
- Reduce interference sources
- Move Raspberry Pi closer
```

## Rollback Procedures

### Firmware Rollback

```bash
# Keep previous firmware versions
cp transmitter_calibration_complete.ino transmitter_v1.0_backup.ino

# To rollback:
1. Open previous version in Arduino IDE
2. Upload to affected sensors
3. Recalibrate
```

### Service Rollback

```bash
# Before updates
sudo cp /home/admin/*.py /home/admin/backup/

# To rollback:
sudo systemctl stop fall-receiver fall-console fall-web
sudo cp /home/admin/backup/*.py /home/admin/
sudo systemctl start fall-receiver fall-console fall-web
```

## Monitoring Deployment

### Real-time Monitoring Dashboard

```bash
# Create monitoring script
nano /home/admin/monitor_system.sh
```

```bash
#!/bin/bash
while true; do
  clear
  echo "=== FALL DETECTION SYSTEM STATUS ==="
  echo "Time: $(date)"
  echo ""
  echo "--- Network Status ---"
  iw dev wlan0 station dump | grep Station | wc -l | xargs echo "Connected Sensors:"
  echo ""
  echo "--- Service Status ---"
  systemctl is-active fall-receiver fall-console fall-web
  echo ""
  echo "--- Recent Falls ---"
  tail -n 5 /home/admin/logs/falls_$(date +%Y-%m-%d).txt
  echo ""
  echo "--- System Resources ---"
  free -h | grep Mem
  df -h | grep root
  vcgencmd measure_temp
  sleep 5
done
```

### Remote Monitoring

```python
# Enable remote access (optional)
# Add to fall_status_socketio.py
app.config['SERVER_NAME'] = '192.168.4.1:5000'

# Access from any device on network:
# http://192.168.4.1:5000
```

## Deployment Validation Criteria

### Acceptance Tests

- [ ] All sensors maintain connection for 24 hours
- [ ] No false positives during normal activities (8 hour test)
- [ ] Fall detection within 100ms (10 controlled tests)
- [ ] Battery life exceeds 20 hours
- [ ] Web interface responsive on multiple devices
- [ ] Logs properly rotate daily
- [ ] System recovers from power loss automatically

### Performance Benchmarks

| Metric | Required | Achieved | Status |
|--------|----------|----------|---------|
| Detection Accuracy | >85% | 88% | ✓ |
| Latency | <100ms | 60ms | ✓ |
| False Positive Rate | <15% | 12% | ✓ |
| Battery Life | >20hr | 24hr | ✓ |
| Uptime | >99% | 99.88% | ✓ |

## Support and Resources

### Documentation
- [GitHub Repository](https://github.com/AlexeyKoz/fall-detection-system)
- [Hardware Setup](02_HARDWARE.md)
- [Algorithm Details](04_ALGORITHMS.md)
- [Performance Metrics](06_PERFORMANCE.md)

### Troubleshooting Resources
- System logs: `/home/admin/logs/`
- Service logs: `journalctl -u fall-*`
- Redis data: `redis-cli MONITOR`

### Contact
- GitHub Issues: [Report problems](https://github.com/AlexeyKoz/fall-detection-system/issues)
- Email: [support email]

---
*End of Deployment Guide - System Ready for Production Use*