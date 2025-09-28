# Hardware Components

## Bill of Materials (BOM)

### Core Components

| Component | Quantity | Specifications | Unit Cost | Total Cost | Supplier |
|-----------|----------|----------------|-----------|------------|----------|
| ESP32 DevKit | 3 | WROOM-32, 4MB Flash | $5 | $15 | AliExpress |
| BNO055 IMU | 3 | 9-DOF, I2C/UART | $30 | $90 | Adafruit |
| Li-Ion Battery | 3 | 3.7V, 1000mAh | $8 | $24 | 18650Store |
| BMS Module | 3 | TP4056, 1A charging | $2 | $6 | AliExpress |
| Raspberry Pi 5 | 1 | 4GB RAM minimum | $80 | $80 | Official |
| MicroSD Card | 1 | 32GB, Class 10 | $10 | $10 | Amazon |
| **Total** | | | | **$225** | |

### Additional Components

| Component | Quantity | Specifications | Purpose |
|-----------|----------|----------------|---------|
| Push Buttons | 6 | Momentary, NO | Power/Calibration |
| LEDs | 12 | 5mm, various colors | Status indicators |
| Resistors | 30 | 220Ω, 10kΩ | LED current limiting, pull-ups |
| Jumper Wires | 1 set | Male-Female, 20cm | Prototyping |
| Breadboard | 3 | 400 points | Prototyping |
| Enclosure | 3 | 70×50×25mm | Weather protection |
| Straps | 3 | Elastic, adjustable | Body mounting |

## Detailed Component Specifications

### ESP32 WROOM-32

**Technical Specifications:**
- **Processor**: Dual-core Xtensa LX6, 240 MHz
- **Memory**: 520 KB SRAM, 4 MB Flash
- **Wireless**: 802.11n WiFi, Bluetooth 4.2
- **GPIO**: 34 programmable pins
- **ADC**: 18 channels, 12-bit
- **Operating Voltage**: 3.3V
- **Current Draw**: 80mA average, 240mA peak
- **Deep Sleep**: 10μA

**Pin Allocation:**
```
GPIO  Function         Connected To
-----------------------------------
21    I2C SDA         BNO055 SDA
22    I2C SCL         BNO055 SCL
2     Status LED      Green LED
32    Yellow LED      Calibration indicator
17    Red LED         Not calibrated
19    Blue LED        Calibrated
5     Green LED       Reserved
14    Power Button    Pull-up to 3.3V
4     Calib Button    Pull-up to 3.3V
```

### BNO055 9-DOF IMU

**Sensor Components:**
- **Accelerometer**: 14-bit, ±2g/±4g/±8g/±16g
- **Gyroscope**: 16-bit, ±125/±250/±500/±1000/±2000 dps
- **Magnetometer**: ~0.3μT resolution
- **Processor**: 32-bit Cortex M0+

**Operating Characteristics:**
- **Voltage**: 3.0-3.6V
- **Current**: 12.3mA normal, 0.04mA sleep
- **Output Rate**: Up to 100Hz
- **Communication**: I2C (up to 400kHz), UART
- **Temperature**: -40°C to +85°C

**Fusion Modes:**
| Mode | Description | Output |
|------|-------------|--------|
| IMU | Accel + Gyro fusion | Relative orientation |
| COMPASS | All sensors | Absolute orientation |
| M4G | Accel + Mag + Gyro | Similar to IMU |
| NDOF | 9-DOF fusion | Absolute orientation |

### Li-Ion Battery System

**Battery Specifications:**
- **Type**: 18650 Li-Ion cell
- **Voltage**: 3.7V nominal, 4.2V max
- **Capacity**: 1000mAh (3.7Wh)
- **Discharge Rate**: 1C continuous
- **Protection**: Over-charge, over-discharge, short circuit
- **Lifetime**: 500+ cycles

**Power Consumption Analysis:**
```
Component         Current    Power     24hr Energy
-------------------------------------------------
ESP32 (active)    80mA      264mW     6.3Wh
ESP32 (sleep)     10μA      33μW      0.8mWh
BNO055           12.3mA     40.6mW    0.97Wh
LEDs (average)    10mA      33mW      0.8Wh
-------------------------------------------------
Total (active)    102.3mA   337.6mW   8.1Wh
Battery Life: ~9.8 hours continuous, 24+ hours with sleep
```

### BMS (Battery Management System)

**TP4056 Module Features:**
- **Charging Current**: 1A maximum
- **Input Voltage**: 4.5-5.5V (USB)
- **Charge Termination**: 4.2V ±1%
- **Protection**: Reverse polarity, over-current
- **Indicators**: Charging (Red), Complete (Blue)
- **Efficiency**: >85%

### Raspberry Pi 5

**Specifications:**
- **CPU**: Quad-core ARM Cortex-A76 @ 2.4GHz
- **GPU**: VideoCore VII
- **RAM**: 4GB/8GB LPDDR4X-4267
- **Storage**: MicroSD (recommended: 32GB+)
- **Network**: Gigabit Ethernet, WiFi 802.11ac
- **USB**: 2×USB 3.0, 2×USB 2.0
- **GPIO**: 40-pin header
- **Power**: 5V/5A via USB-C

## Wiring Diagrams

### Sensor Node Wiring

```
ESP32 WROOM-32 Pinout
                    ┌─────────┐
               EN ──┤1      38├── GPIO23
            GPIO36 ──┤2      37├── GPIO22 ─── BNO055 SCL
            GPIO39 ──┤3      36├── GPIO1
            GPIO34 ──┤4      35├── GPIO3
            GPIO35 ──┤5      34├── GPIO21 ─── BNO055 SDA
            GPIO32 ──┤6 ⚡   33├── GND ────── BNO055 GND
            GPIO33 ──┤7      32├── GPIO19 ─── Blue LED
            GPIO25 ──┤8      31├── GPIO18
            GPIO26 ──┤9      30├── GPIO5 ──── Green LED
            GPIO27 ──┤10     29├── GPIO17 ─── Red LED
            GPIO14 ──┤11     28├── GPIO16
            GPIO12 ──┤12     27├── GPIO4 ──── Calib Button
               GND ──┤13     26├── GPIO0
            GPIO13 ──┤14     25├── GPIO2 ──── Status LED
             GPIO9 ──┤15     24├── GPIO15
            GPIO10 ──┤16     23├── GPIO8
            GPIO11 ──┤17     22├── GPIO7
               VIN ──┤18     21├── GPIO6
              3.3V ──┤19     20├── GND
                    └─────────┘
```

### BNO055 Connection

```
BNO055 Module
┌──────────────┐
│ ○ VIN   3.3V │───── ESP32 3.3V
│ ○ GND   GND  │───── ESP32 GND
│ ○ SDA   SDA  │───── ESP32 GPIO21
│ ○ SCL   SCL  │───── ESP32 GPIO22
│ ○ RST   ---  │      (Not connected)
│ ○ ADR   GND  │───── GND (I2C addr: 0x28)
│ ○ INT   ---  │      (Optional interrupt)
│ ○ PS0   ---  │      (Protocol select)
│ ○ PS1   ---  │      (Protocol select)
└──────────────┘
```

### LED Circuit

```
ESP32 GPIO ──┬── 220Ω ──┬── LED ──┬── GND
             │           │         │
            3.3V      Anode    Cathode
```

### Button Circuit

```
3.3V ──┬── 10kΩ ──┬── ESP32 GPIO
       │          │
       └─ Button ─┴── GND
```

## Assembly Instructions

### Step 1: ESP32 Preparation
1. Solder headers to ESP32 if needed
2. Flash firmware before assembly
3. Test WiFi connectivity
4. Verify deep sleep functionality

### Step 2: Sensor Connection
1. Connect BNO055 via I2C:
   - VIN to 3.3V (NOT 5V!)
   - GND to GND
   - SDA to GPIO21
   - SCL to GPIO22
2. Add 4.7kΩ pull-up resistors on SDA/SCL
3. Ground ADR pin for address 0x28

### Step 3: Power System
1. Connect battery to BMS B+ and B-
2. Connect BMS OUT+ to ESP32 VIN
3. Connect BMS OUT- to ESP32 GND
4. Add power switch between BMS and ESP32
5. Connect USB to BMS for charging

### Step 4: User Interface
1. Install power button on GPIO14 with pull-up
2. Install calibration button on GPIO4 with pull-up
3. Connect status LEDs with current limiting resistors
4. Test all LEDs and buttons

### Step 5: Enclosure
1. Use weather-resistant box (IP54 minimum)
2. Drill holes for buttons and LEDs
3. Add cable glands for sensor wires
4. Include ventilation for heat dissipation
5. Secure battery with foam padding

## Mechanical Design

### Mounting Considerations
- **Orientation**: Y-axis vertical when worn
- **Stability**: Minimize movement relative to body
- **Comfort**: Soft padding against skin
- **Adjustability**: Elastic straps for different body sizes

### Recommended Positions
| Sensor | Location | Mounting Method |
|--------|----------|-----------------|
| 1 | Chest/Sternum | Chest strap or vest |
| 2 | Hip/Waist | Belt clip or waistband |
| 3 | Thigh | Elastic band or pocket |

## Testing Procedures

### Component Testing
1. **ESP32 Test**: Upload blink sketch
2. **BNO055 Test**: Run I2C scanner
3. **Battery Test**: Measure voltage (3.7-4.2V)
4. **LED Test**: Individual GPIO control
5. **Button Test**: Serial monitor debounce

### Integration Testing
1. Power consumption measurement
2. WiFi range testing
3. Sensor calibration verification
4. Battery life validation
5. Temperature stress testing

## Troubleshooting Hardware Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| BNO055 not detected | Wrong I2C address | Check ADR pin grounding |
| ESP32 won't boot | Insufficient power | Check battery voltage |
| WiFi disconnections | Poor antenna | Add external antenna |
| LEDs not working | Wrong polarity | Check LED orientation |
| Buttons unresponsive | Missing pull-up | Add 10kΩ resistor |
| Short battery life | High current draw | Implement deep sleep |

---
*Next: [Software Stack](03_SOFTWARE.md)*