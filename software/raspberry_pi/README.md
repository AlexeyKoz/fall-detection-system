# Raspberry Pi Software Installation Guide

## Overview

This directory contains the Python-based fall detection processing system that runs on the Raspberry Pi. The system receives sensor data via UDP, processes it through Redis, and provides real-time monitoring through console and web interfaces.

## System Requirements

### Hardware
- Raspberry Pi 4 or 5 (minimum 2GB RAM, 4GB recommended)
- 32GB microSD card (Class 10 or better)
- Official 5V/3A power supply
- Active cooling recommended for continuous operation

### Operating System
- Raspberry Pi OS (64-bit) Lite or Desktop
- Kernel version 5.15 or newer
- Python 3.7 or higher

## Quick Installation

Run the automated installation script:
```bash
cd software/raspberry_pi
chmod +x scripts/setup_fallnet.sh
sudo bash scripts/setup_fallnet.sh
```

## Manual Installation

### Step 1: System Update

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    redis-server \
    hostapd \
    dnsmasq \
    git \
    vim \
    htop \
    screen
```

### Step 2: Network Configuration (Access Point)

#### Configure hostapd
```bash
sudo nano /etc/hostapd/hostapd.conf
```

Add the following content:
```
interface=wlan0
driver=nl80211
ssid=FallNet
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=1122334455
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

#### Configure DHCP Server
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
```

Add:
```
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

#### Set Static IP
```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:
```
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

#### Enable Services
```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd dnsmasq
sudo systemctl start hostapd dnsmasq
```

### Step 3: Python Environment Setup

```bash
# Create virtual environment
python3 -m venv ~/venv

# Activate virtual environment
source ~/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Redis Configuration

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings to modify:
# bind 127.0.0.1 ::1
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save ""  # Disable persistence for performance

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Step 5: Service Installation

Create systemd service files:

#### UDP Receiver Service
```bash
sudo nano /etc/systemd/system/fall-receiver.service
```

```ini
[Unit]
Description=Fall Detection UDP Receiver
After=network.target redis.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fall-detection-system/software/raspberry_pi
Environment="PATH=/home/pi/venv/bin"
ExecStart=/home/pi/venv/bin/python src/fall_receiver_redis.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Console Monitor Service
```bash
sudo nano /etc/systemd/system/fall-console.service
```

```ini
[Unit]
Description=Fall Detection Console Monitor
After=fall-receiver.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fall-detection-system/software/raspberry_pi
Environment="PATH=/home/pi/venv/bin"
ExecStart=/home/pi/venv/bin/python src/fall_detector_console.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Web Interface Service
```bash
sudo nano /etc/systemd/system/fall-web.service
```

```ini
[Unit]
Description=Fall Detection Web Interface
After=fall-receiver.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fall-detection-system/software/raspberry_pi
Environment="PATH=/home/pi/venv/bin"
ExecStart=/home/pi/venv/bin/python src/fall_status_socketio.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable fall-receiver fall-console fall-web
sudo systemctl start fall-receiver fall-console fall-web
```

## Configuration

### Network Configuration
Edit `../config/network_config.json` to modify:
- WiFi credentials
- UDP port (default: 12345)
- WebSocket port (default: 5000)
- IP ranges

### Detection Thresholds
Edit `../config/thresholds.json` to adjust:
- Fall detection sensitivity
- Warning thresholds
- Algorithm parameters
- User profiles (elderly, adult, clinical)

## Usage

### Starting the System

#### Automatic Start (Recommended)
```bash
cd scripts
./autostart_fall_system.sh
```

#### Manual Start
```bash
# Start each service individually
sudo systemctl start fall-receiver
sudo systemctl start fall-console
sudo systemctl start fall-web
```

### Monitoring

#### Check Service Status
```bash
sudo systemctl status fall-receiver
sudo systemctl status fall-console
sudo systemctl status fall-web
```

#### View Logs
```bash
# Service logs
journalctl -u fall-receiver -f
journalctl -u fall-console -f
journalctl -u fall-web -f

# Application logs
tail -f ~/logs/falls_$(date +%Y-%m-%d).txt
```

#### Console Monitor
The console monitor displays real-time sensor status:
```bash
python src/fall_detector_console.py
```

Output format:
```
========== STATUS @ 2024-12-08 15:45:10 ==========
Sensor 1 [192.168.4.10]: ✅
  Gyro: [ 0.145 -0.067  0.089]  Accel: [ 0.456 -0.234  9.812]
  Fall Index: 0.18  
Sensor 2 [192.168.4.11]: ✅
  Gyro: [ 0.234  0.156 -0.089]  Accel: [ 0.678  0.345  9.756]
  Fall Index: 0.30  
Sensor 3 [192.168.4.12]: ❌ No data
============================
```

### Web Interface

Access the web interface:
- Local: http://localhost:5000
- Network: http://192.168.4.1:5000

The interface shows:
- Real-time fall status (GREEN: Stable, RED: Fall)
- Automatic updates via WebSocket
- Full-screen mode available

## File Structure

```
raspberry_pi/
├── src/                        # Python source files
│   ├── fall_receiver_redis.py # UDP receiver service
│   ├── fall_detector_console.py # Console monitor
│   └── fall_status_socketio.py # Web interface
├── scripts/                    # Shell scripts
│   ├── setup_fallnet.sh       # Network setup
│   └── autostart_fall_system.sh # System startup
├── web/                        # Web assets
│   └── socket.io.min.js       # WebSocket client
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| No WiFi network "FallNet" | Check hostapd status: `sudo systemctl status hostapd` |
| Sensors not connecting | Verify DHCP is running: `sudo systemctl status dnsmasq` |
| Redis connection error | Check Redis: `redis-cli ping` (should return PONG) |
| Web interface not accessible | Check firewall: `sudo ufw status` |
| Services not starting | Check logs: `journalctl -xe` |

### Debug Commands

```bash
# Check network configuration
ip addr show wlan0
iw dev wlan0 info

# Monitor UDP traffic
sudo tcpdump -i wlan0 -n udp port 12345

# Check connected devices
arp -a

# Monitor Redis
redis-cli monitor

# System resources
htop
df -h
free -h
```

### Reset Services

```bash
# Restart all services
sudo systemctl restart fall-receiver fall-console fall-web

# Clear Redis data
redis-cli FLUSHALL

# Reset network
sudo systemctl restart hostapd dnsmasq
```

## Performance Optimization

### Reduce CPU Usage
```bash
# Set CPU governor to performance mode
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Increase UDP Buffer
```bash
sudo sysctl -w net.core.rmem_max=26214400
sudo sysctl -w net.core.rmem_default=26214400
```

### Disable Swap (if sufficient RAM)
```bash
sudo dphys-swapfile swapoff
sudo systemctl disable dphys-swapfile
```

## Backup and Recovery

### Backup Configuration
```bash
# Create backup directory
mkdir -p ~/backups

# Backup script
tar -czf ~/backups/fall-detection-backup-$(date +%Y%m%d).tar.gz \
    /etc/hostapd/hostapd.conf \
    /etc/dnsmasq.conf \
    /etc/systemd/system/fall-*.service \
    ~/fall-detection-system/software/config/
```

### Restore Configuration
```bash
# Restore from backup
tar -xzf ~/backups/fall-detection-backup-YYYYMMDD.tar.gz -C /
sudo systemctl daemon-reload
sudo systemctl restart fall-receiver fall-console fall-web
```

## Development

### Running in Development Mode

```bash
# Activate virtual environment
source ~/venv/bin/activate

# Run with debug output
FLASK_ENV=development python src/fall_status_socketio.py

# Run with custom config
python src/fall_receiver_redis.py --config ../config/network_config.json
```

### Running Tests

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## Security Considerations

1. **Change default WiFi password** in `/etc/hostapd/hostapd.conf`
2. **Enable firewall** with only necessary ports open
3. **Regular updates**: `sudo apt update && sudo apt upgrade`
4. **Monitor logs** for suspicious activity
5. **Backup regularly** to prevent data loss

## Support

- GitHub Issues: https://github.com/AlexeyKoz/fall-detection-system/issues
- Documentation: See main [README.md](../../README.md)
- Logs location: `~/logs/` and `/var/log/syslog`

---
*Part of the Fall Detection System - Ariel University Final Year Project*