# Raspberry Pi Setup

## System Requirements

### Hardware Requirements
- **Model**: Raspberry Pi 4/5 (minimum 2GB RAM)
- **Storage**: 32GB microSD card (Class 10 or better)
- **Power**: Official 5V/3A USB-C power supply
- **Cooling**: Heatsinks or fan recommended

### Operating System
- **OS**: Raspberry Pi OS (64-bit) Lite or Desktop
- **Version**: Bullseye or newer
- **Kernel**: 5.15+

## Initial Setup

### 1. OS Installation

```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Flash OS to SD card with settings:
# - Enable SSH
# - Set hostname: falldetector
# - Configure WiFi (temporary)
# - Set user: admin
```

### 2. First Boot Configuration

```bash
# Connect via SSH
ssh admin@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    redis-server \
    hostapd \
    dnsmasq \
    git \
    vim \
    htop \
    screen
```

### 3. Network Configuration

#### Access Point Setup

**Create hostapd configuration:**
```bash
sudo nano /etc/hostapd/hostapd.conf
```

```conf
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

**Configure hostapd daemon:**
```bash
sudo nano /etc/default/hostapd
```
```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

#### DHCP Server Setup

**Configure dnsmasq:**
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
```

```conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/gw.wlan/192.168.4.1
```

#### Static IP Configuration

**Edit dhcpcd.conf:**
```bash
sudo nano /etc/dhcpcd.conf
```

```conf
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

#### Enable Services

```bash
# Unmask and enable services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

# Start services
sudo systemctl start hostapd
sudo systemctl start dnsmasq

# Check status
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

## Software Installation

### 1. Python Environment

```bash
# Create project directory
mkdir -p /home/admin/fall-detection
cd /home/admin/fall-detection

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

**Create requirements.txt:**
```bash
nano requirements.txt
```

```
redis==4.5.1
flask==2.3.2
flask-socketio==5.3.4
python-socketio==5.9.0
numpy==1.24.3
eventlet==0.33.3
```

**Install packages:**
```bash
pip install -r requirements.txt
```

### 3. Redis Configuration

**Edit Redis config:**
```bash
sudo nano /etc/redis/redis.conf
```

Key settings:
```conf
# Bind to localhost only
bind 127.0.0.1 ::1

# Disable persistence (optional for performance)
save ""

# Set max memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable keyspace notifications
notify-keyspace-events Ex
```

**Restart Redis:**
```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 4. Deploy Application Files

```bash
# Clone repository
git clone https://github.com/AlexeyKoz/fall-detection-system.git
cd fall-detection-system

# Copy Python files
cp software/raspberry_pi/src/*.py /home/admin/
cp software/raspberry_pi/scripts/*.sh /home/admin/
chmod +x /home/admin/*.sh

# Create log directory
mkdir -p /home/admin/logs
```

## Service Configuration

### 1. Create Systemd Services

**UDP Receiver Service:**
```bash
sudo nano /etc/systemd/system/fall-receiver.service
```

```ini
[Unit]
Description=Fall Detection UDP Receiver
After=network.target redis.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin
Environment="PATH=/home/admin/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/admin/venv/bin/python /home/admin/fall_receiver_redis.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Console Monitor Service:**
```bash
sudo nano /etc/systemd/system/fall-console.service
```

```ini
[Unit]
Description=Fall Detection Console Monitor
After=fall-receiver.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin
Environment="PATH=/home/admin/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/admin/venv/bin/python /home/admin/fall_detector_console.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Web Interface Service:**
```bash
sudo nano /etc/systemd/system/fall-web.service
```

```ini
[Unit]
Description=Fall Detection Web Interface
After=fall-receiver.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin
Environment="PATH=/home/admin/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/admin/venv/bin/python /home/admin/fall_status_socketio.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable fall-receiver.service
sudo systemctl enable fall-console.service
sudo systemctl enable fall-web.service

# Start services
sudo systemctl start fall-receiver.service
sudo systemctl start fall-console.service
sudo systemctl start fall-web.service

# Check status
sudo systemctl status fall-receiver.service
sudo systemctl status fall-console.service
sudo systemctl status fall-web.service
```

## Auto-Start Configuration

### 1. Boot Script

**Create auto-start script:**
```bash
nano /home/admin/autostart_fall_system.sh
```

```bash
#!/bin/bash
# Wait for network
sleep 10

# Check Redis
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start services if not running
sudo systemctl start fall-receiver.service
sudo systemctl start fall-console.service
sudo systemctl start fall-web.service

# Optional: Launch browser in kiosk mode (if desktop environment)
if [ -n "$DISPLAY" ]; then
    chromium-browser --kiosk --start-fullscreen http://localhost:5000 &
fi
```

### 2. Crontab Entry

```bash
# Edit crontab
crontab -e

# Add line:
@reboot /home/admin/autostart_fall_system.sh
```

## Performance Optimization

### 1. CPU Governor

```bash
# Set performance mode
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make permanent
sudo nano /etc/rc.local
# Add before 'exit 0':
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 2. Network Optimization

```bash
# Increase UDP buffer sizes
sudo nano /etc/sysctl.conf
```

Add:
```conf
# UDP buffer sizes
net.core.rmem_max=26214400
net.core.rmem_default=26214400
net.core.wmem_max=26214400
net.core.wmem_default=26214400
net.core.netdev_max_backlog=5000
```

Apply:
```bash
sudo sysctl -p
```

### 3. Redis Optimization

```bash
# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# Add to /etc/rc.local for persistence
echo never > /sys/kernel/mm/transparent_hugepage/enabled
```

## Monitoring and Maintenance

### 1. System Monitoring

```bash
# Install monitoring tools
sudo apt install -y iotop nmon lm-sensors

# Monitor resources
htop  # CPU and memory
iotop  # Disk I/O
nmon  # Network monitoring

# Check temperatures
vcgencmd measure_temp
```

### 2. Log Management

**Configure log rotation:**
```bash
sudo nano /etc/logrotate.d/falldetection
```

```
/home/admin/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 admin admin
    postrotate
        systemctl reload fall-receiver.service
    endscript
}
```

### 3. Backup Configuration

```bash
# Backup script
nano /home/admin/backup_config.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/admin/backups"
mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_$(date +%Y%m%d).tar.gz \
    /etc/hostapd/hostapd.conf \
    /etc/dnsmasq.conf \
    /etc/redis/redis.conf \
    /home/admin/*.py \
    /home/admin/*.sh

# Keep only last 7 backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

| Issue | Command | Solution |
|-------|---------|----------|
| No WiFi AP | `sudo systemctl status hostapd` | Check config, restart service |
| No DHCP | `sudo systemctl status dnsmasq` | Verify interface, restart |
| Redis error | `redis-cli ping` | Should return PONG |
| Service fails | `journalctl -u fall-receiver` | Check logs for errors |
| High CPU | `htop` | Check for runaway processes |

### Diagnostic Commands

```bash
# Check network status
ip addr show wlan0
iw dev wlan0 info
hostapd_cli status

# Check connected devices
arp -a
dhcp-lease-list

# Test UDP reception
nc -ul 12345

# Monitor Redis
redis-cli monitor
redis-cli INFO stats

# Service logs
journalctl -f -u fall-receiver
journalctl -f -u fall-web
journalctl -f -u fall-console

# System resources
free -h
df -h
uptime
```

### Reset Procedures

```bash
# Reset WiFi
sudo systemctl restart hostapd dnsmasq

# Reset services
sudo systemctl restart fall-receiver fall-console fall-web

# Clear Redis
redis-cli FLUSHALL

# Full system reset
sudo reboot
```

---
*Next: [Performance Metrics](06_PERFORMANCE.md)*