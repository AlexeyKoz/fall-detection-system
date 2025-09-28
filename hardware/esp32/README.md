# ESP32 Firmware Flashing Guide / Инструкция по прошивке ESP32

## Prerequisites / Требования

### Hardware Requirements / Аппаратные требования
- ESP32 DevKit (WROOM-32 recommended)
- USB cable (micro-USB or USB-C depending on your board)
- Computer with USB port

### Software Requirements / Программные требования
1. **Arduino IDE** (version 1.8.19 or 2.x)
   - Download: https://www.arduino.cc/en/software

2. **ESP32 Board Package**
   - Install via Board Manager

3. **Required Libraries / Необходимые библиотеки**:
   - Adafruit BNO055
   - Adafruit Unified Sensor
   - WiFi (built-in)
   - Wire (built-in)
   - EEPROM (built-in)

## Step 1: Arduino IDE Setup / Настройка Arduino IDE

### 1.1 Install Arduino IDE
```bash
# For Ubuntu/Debian:
sudo apt update
sudo apt install arduino

# For Windows/Mac:
# Download from https://www.arduino.cc/en/software
```

### 1.2 Add ESP32 Board Support / Добавление поддержки ESP32

1. Open Arduino IDE
2. Go to **File → Preferences** (Arduino → Preferences on Mac)
3. Add to **Additional Board Manager URLs**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click **OK**

### 1.3 Install ESP32 Board Package

1. Go to **Tools → Board → Board Manager**
2. Search for "ESP32"
3. Install **"esp32 by Espressif Systems"** (version 2.0.11 or later)
4. Wait for installation to complete

## Step 2: Library Installation / Установка библиотек

### Method 1: Using Library Manager (Recommended)

1. Go to **Tools → Manage Libraries**
2. Search and install:
   - **Adafruit BNO055** (by Adafruit)
   - **Adafruit Unified Sensor** (by Adafruit)

### Method 2: Manual Installation

```bash
# Navigate to Arduino libraries folder
# Windows: Documents\Arduino\libraries
# Mac: ~/Documents/Arduino/libraries
# Linux: ~/Arduino/libraries

# Clone libraries
git clone https://github.com/adafruit/Adafruit_BNO055.git
git clone https://github.com/adafruit/Adafruit_Sensor.git
```

## Step 3: Hardware Configuration / Настройка оборудования

### 3.1 Wiring Diagram / Схема подключения

```
ESP32          BNO055
------         -------
3.3V    →      VIN
GND     →      GND
GPIO21  →      SDA
GPIO22  →      SCL

ESP32          LEDs           Buttons
------         ----           -------
GPIO2   →      Status LED     
GPIO32  →      Yellow LED     
GPIO17  →      Red LED        
GPIO19  →      Blue LED       
GPIO5   →      Green LED      
GPIO14  ←                     Power Button (with pull-up)
GPIO4   ←                     Calibration Button (with pull-up)
```

### 3.2 Important Notes / Важные замечания

- Use 3.3V for BNO055, NOT 5V
- Add 10kΩ pull-up resistors to button inputs
- LEDs should have current-limiting resistors (220Ω - 1kΩ)

## Step 4: Code Configuration / Настройка кода

### 4.1 Open the Firmware

1. Open `transmitter_calibration_complete.ino` in Arduino IDE
2. Configure board-specific settings:

```cpp
// === CONFIG === 
// IMPORTANT: Change boardNumber for each sensor node!
const int boardNumber = 1;  // Change to 1, 2, or 3 for each ESP32

// Network settings (same for all nodes)
const char* ssid = "FallNet";
const char* password = "1122334455";
const char* raspberry_ip = "192.168.4.1";
const int udp_port = 12345;
```

### 4.2 Board Number Assignment / Назначение номеров плат

| Sensor Location | Board Number | Recommended Position |
|-----------------|--------------|---------------------|
| Chest/Thoracic  | 1           | Upper torso         |
| Hip/Waist       | 2           | Center of mass      |
| Knee/Thigh      | 3           | Lower body          |

## Step 5: Upload Firmware / Загрузка прошивки

### 5.1 Select Board and Port

1. **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
2. **Tools → Port → [Your COM port]**
   - Windows: `COM3`, `COM4`, etc.
   - Mac/Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`

### 5.2 Board Settings / Настройки платы

Configure in **Tools** menu:

| Parameter | Value |
|-----------|-------|
| Board | ESP32 Dev Module |
| Upload Speed | 921600 |
| CPU Frequency | 240MHz (WiFi/BT) |
| Flash Frequency | 80MHz |
| Flash Mode | QIO |
| Flash Size | 4MB (32Mb) |
| Partition Scheme | Default 4MB with spiffs |
| Core Debug Level | None |
| PSRAM | Disabled |

### 5.3 Upload Process / Процесс загрузки

1. Click **Upload** button (→) or press `Ctrl+U`
2. Wait for compilation
3. **IMPORTANT**: Some ESP32 boards require holding the **BOOT** button during upload:
   - Press and hold **BOOT** button
   - When you see "Connecting..." in console
   - Release after 2-3 seconds

### 5.4 Expected Upload Output

```
Sketch uses 875426 bytes (66%) of program storage space.
Global variables use 38140 bytes (11%) of dynamic memory.

esptool.py v3.3
Serial port COM4
Connecting........_____....
Chip is ESP32-D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz
Uploading stub...
Writing at 0x00001000... (100%)
Wrote 875426 bytes

Hard resetting via RTS pin...
```

## Step 6: Verification / Проверка

### 6.1 Open Serial Monitor

1. **Tools → Serial Monitor** or press `Ctrl+Shift+M`
2. Set baud rate to **115200**
3. You should see:

```
🔌 Connecting to Wi-Fi...
✅ Wi-Fi Connected!
📡 IP: 192.168.4.10
✅ BNO055 connected.
```

### 6.2 LED Test Sequence

Upon successful boot:
1. All LEDs turn ON for 5 seconds (test mode)
2. All LEDs turn OFF
3. Status LED (GPIO2) stays ON when connected

## Step 7: Calibration / Калибровка

### 7.1 Initial Calibration

1. **Long press** calibration button (3 seconds)
2. Yellow LED starts blinking
3. Rotate sensor slowly in figure-8 pattern
4. Blue LED turns ON when calibration complete
5. Calibration automatically saved to EEPROM

### 7.2 Check Calibration Status

- **Short press** calibration button
- LEDs show status for 5 seconds:
  - 🔴 **Red LED**: Not calibrated
  - 🔵 **Blue LED**: Fully calibrated

## Troubleshooting / Решение проблем

### Common Issues and Solutions

| Problem | Solution |
|---------|----------|
| **"Failed to connect to ESP32"** | Hold BOOT button during upload |
| **"No module named 'serial'"** | Install pyserial: `pip install pyserial` |
| **"BNO055 not detected"** | Check I2C connections (SDA/SCL) |
| **"WiFi not connecting"** | Verify SSID and password in code |
| **LEDs not working** | Check resistors and GPIO connections |
| **Upload speed errors** | Reduce upload speed to 115200 |

### Serial Monitor Debug Commands

While connected to Serial Monitor, you can monitor:
- Sensor data stream
- WiFi connection status
- Calibration values
- Real-time gyro/accel readings

### Deep Sleep Mode

- **Activate**: Hold power button 3 seconds
- **Wake**: Press power button once
- Status LED turns OFF in sleep mode

## Advanced Configuration / Расширенная настройка

### Custom Network Settings

```cpp
// For different network
const char* ssid = "YourNetworkName";
const char* password = "YourPassword";

// For different Raspberry Pi IP
const char* raspberry_ip = "192.168.1.100";
```

### Calibration Persistence

Calibration data is automatically saved to EEPROM addresses 1-64:
- Survives power cycles
- No need to recalibrate after restart
- Clear with: `EEPROM.put(1, 0);`

## Platform-Specific Notes

### Windows
- Install CH340/CP2102 drivers if needed
- Use Device Manager to find COM port

### macOS
- Install Silicon Labs CP2102 driver
- Port appears as `/dev/cu.SLAB_USBtoUART`

### Linux
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Log out and back in for changes to take effect

## Version Information

- **Firmware Version**: 1.0
- **Compatible ESP32 Core**: 2.0.x
- **BNO055 Library**: 1.6.0+
- **Arduino IDE**: 1.8.19+ or 2.x

## Support and Documentation

- [ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/)
- [BNO055 Datasheet](https://www.bosch-sensortec.com/products/smart-sensors/bno055/)
- [Project Repository](https://github.com/AlexeyKoz/fall-detection-system)

## License

MIT License - See LICENSE file for details

---
*Last Updated: 2024*