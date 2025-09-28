# Fall Detection System for Elderly Care

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-ESP32%20|%20RPi-green.svg)](https://www.espressif.com/en/products/socs/esp32)

Real-time fall detection and prediction system using IMU sensors and machine learning algorithms.

## 📋 Project Information

- **Institution**: Ariel University  
- **Project Type**: Final Year Project  
- **Year**: 2024
- **Primary Goal**: Early fall detection for elderly individuals using mathematical modeling and real-time sensor data analysis

## 🎯 Features

- **Early Fall Prediction**: 300-500ms warning before impact
- **88% Accuracy**: Validated on real-world datasets
- **Wireless Operation**: No cables required
- **24-Hour Battery Life**: Continuous monitoring
- **Real-time Alerts**: WebSocket-based instant notifications

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlexeyKoz/fall-detection-system.git
   cd fall-detection-system
   ```

2. **Setup Hardware**
   - Flash ESP32 nodes with firmware (see [Flashing Guide](docs/FLASHING_GUIDE.md))
   - Configure board numbers (1, 2, 3) for each sensor
   - Connect BNO055 sensors via I2C

3. **Setup Raspberry Pi**
   ```bash
   # Configure network as access point
   sudo bash software/raspberry_pi/scripts/setup_fallnet.sh
   
   # Install Python dependencies
   pip install -r software/raspberry_pi/requirements.txt
   ```

4. **Start the System**
   ```bash
   ./autostart_fall_system.sh
   ```

5. **Access Web Interface**
   - Open browser: `http://192.168.4.1:5000`

## 📚 Documentation

- **[Technical Overview](docs/TECHNICAL_OVERVIEW.md)** - Complete system details
- **[Architecture](docs/01_ARCHITECTURE.md)** - System design and data flow
- **[Hardware Setup](docs/02_HARDWARE.md)** - Component assembly guide
- **[Software Stack](docs/03_SOFTWARE.md)** - Software configuration
- **[Algorithms](docs/04_ALGORITHMS.md)** - Fall detection mathematics
- **[Raspberry Pi Setup](docs/05_RASPBERRY_PI.md)** - RPi configuration
- **[Performance](docs/06_PERFORMANCE.md)** - System metrics
- **[Deployment Guide](docs/07_DEPLOYMENT.md)** - Production deployment

## 🔬 Based on Research

This project implements the mathematical model described in:
> Mohammed, S. H., et al. (2024). "A Mathematical Model for Fall Detection Prediction in Elderly People." 
> IEEE Sensors Journal, vol. 24, no. 20, pp. 32981-32990.

## 🛠️ System Requirements

### Hardware
- 3× ESP32 WROOM-32 Development Boards
- 3× BNO055 9-DOF IMU Sensors  
- 1× Raspberry Pi 4/5 (4GB+ RAM)
- 3× Li-Ion Batteries (1000mAh)
- LEDs, buttons, resistors (see [BOM](hardware/bom.csv))

### Software
- Arduino IDE 1.8.19+ (for ESP32)
- Python 3.7+ (for Raspberry Pi)
- Redis Server
- Required libraries listed in respective folders

## 📂 Repository Structure

```
fall-detection-system/
├── README.md                    # Project overview and quick start
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
│
├── docs/                        # Documentation
│   ├── HARDWARE_SETUP.md       # Hardware assembly guide
│   ├── CALIBRATION_GUIDE.md    # Sensor calibration procedures
│   ├── API_REFERENCE.md        # API documentation
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   └── images/                 # Diagrams and photos
│       ├── system_architecture.png
│       ├── wiring_diagram.png
│       └── sensor_placement.jpg
│
├── hardware/                    # Hardware components
│   ├── esp32/                  # ESP32 firmware
│   │   ├── src/
│   │   │   └── transmitter_calibration_complete.ino
│   │   ├── lib/                # Required libraries
│   │   └── README.md           # Flashing instructions
│   ├── schematics/             # Circuit diagrams
│   │   ├── esp32_bno055_connection.pdf
│   │   └── power_system.pdf
│   └── bom.csv                 # Bill of Materials
│
├── software/                    # Software components
│   ├── raspberry_pi/           # Raspberry Pi code
│   │   ├── src/                # Python services
│   │   │   ├── fall_receiver_redis.py
│   │   │   ├── fall_detector_console.py
│   │   │   └── fall_status_socketio.py
│   │   ├── web/                # Web assets
│   │   │   └── socket.io.min.js
│   │   ├── scripts/            # Setup scripts
│   │   │   ├── setup_fallnet.sh
│   │   │   └── autostart_fall_system.sh
│   │   ├── requirements.txt    # Python dependencies
│   │   └── README.md           # Installation guide
│   └── config/                 # Configuration files
│       ├── network_config.json
│       └── thresholds.json
│
├── research/                    # Research materials
│   ├── papers/
│   │   └── IEEE_Fall_Detection_Model_2024.pdf
│   └── datasets/
│       └── README.md           # Dataset information
│
├── tests/                      # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── test_data/              # Test datasets
│
└── examples/                   # Usage examples
    ├── single_sensor_demo/     # Single sensor example
    └── multi_sensor_setup/     # Multi-sensor example
```

## 👥 Contributors

- **[Alexey Kozlov](https://github.com/AlexeyKoz)** - System Architecture & Hardware Development
- **Gavriel Shavchuk** - Algorithm Enhancement & Project Management

## 🤝 Acknowledgments

- Ariel University - For project support and resources
- Mohammed et al. - For the foundational research paper
- Open source community - For libraries and tools

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/AlexeyKoz/fall-detection-system/issues)
- **Email**: AL7koz@gmail.com

---
*Developed at Ariel University as a Final Year Project (2024)*