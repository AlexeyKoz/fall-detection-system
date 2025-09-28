// === Fall Detector with Calibration LEDs and Save Calibration ===
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <WiFiUdp.h>
#include <EEPROM.h>

// === CONFIG ===
const char* ssid = "FallNet";
const char* password = "1122334455";
const char* raspberry_ip = "192.168.4.1";
const int udp_port = 12345;
const int boardNumber = 2;

#define BUTTON_PIN 14       // Кнопка сна
#define LED_PIN 2           // Светодиод статуса
#define CALIB_BUTTON_PIN 4  // Кнопка калибровки

#define LED_YELLOW 32       // Мигает при калибровке
#define LED_RED 17          // Не откалиброван
#define LED_BLUE 19         // Откалиброван полностью
#define LED_GREEN 5

WiFiUDP udp;
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29);

unsigned long lastSendTime = 0;
unsigned long lastLogTime = 0;
unsigned long buttonPressStart = 0;
unsigned long calibPressStart = 0;
unsigned long lastBlink = 0;
bool wifiReported = false;
bool sensorReported = false;
bool isCalibrating = false;
bool ledState = false;

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(CALIB_BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);

  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_PIN, HIGH); // включение статуса

  digitalWrite(LED_YELLOW, HIGH);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_BLUE, HIGH);
  digitalWrite(LED_GREEN, HIGH);
  delay(5000);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_GREEN, LOW);

  if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT0) {
    Serial.println("🌙 Wake from deep sleep");
  }

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);
  Serial.println("🔌 Connecting to Wi-Fi...");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.printf("Attempt %d — Status: %d\n", ++attempts, WiFi.status());
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✅ Wi-Fi Connected!");
    Serial.print("📡 IP: "); Serial.println(WiFi.localIP());
    wifiReported = true;
  }

  Wire.begin();
  if (!bno.begin()) {
    Serial.println("❌ BNO055 not detected!");
    while (1);
  }
  Serial.println("✅ BNO055 connected.");
  sensorReported = true;

  EEPROM.begin(64);
  adafruit_bno055_offsets_t calibrationData;
  EEPROM.get(1, calibrationData);
  if (calibrationData.accel_offset_x != 0 || calibrationData.gyro_offset_x != 0) {
    bno.setSensorOffsets(calibrationData);
    Serial.println("✅ Calibration offsets loaded from EEPROM.");
  }
}

void updateCalibLEDs(uint8_t gyro, uint8_t accel) {
  bool calibrated = (gyro == 3 && accel == 3);
  digitalWrite(LED_RED, calibrated ? LOW : HIGH);
  digitalWrite(LED_BLUE, calibrated ? HIGH : LOW);
}

void handleCalibrationButton() {
  static bool ledState = false;
  static unsigned long lastBlink = 0;

  bool buttonPressed = digitalRead(CALIB_BUTTON_PIN) == LOW;

  if (buttonPressed) {
    if (calibPressStart == 0) calibPressStart = millis();
    else if (millis() - calibPressStart > 3000) {
      if (!isCalibrating) {
        Serial.println("🧭 Starting manual calibration...");
        isCalibrating = true;
      } else {
        Serial.println("🧭 Calibration manually stopped by user.");
        isCalibrating = false;
        digitalWrite(LED_YELLOW, LOW);
      }
      calibPressStart = 0;
    }
  } else {
    if (calibPressStart > 0 && millis() - calibPressStart < 3000 && !isCalibrating) {
      uint8_t sys, gyro, accel, mag;
      bno.getCalibration(&sys, &gyro, &accel, &mag);
      updateCalibLEDs(gyro, accel);
      Serial.printf("🧭 Calib status: Gyro=%d, Accel=%d (ignore Mag=%d)\n", gyro, accel, mag);
      delay(5000);
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_BLUE, LOW);
    }
    calibPressStart = 0;
  }

  if (isCalibrating) {
    if (millis() - lastBlink > 300) {
      ledState = !ledState;
      digitalWrite(LED_YELLOW, ledState);
      lastBlink = millis();
    }

    uint8_t sys, gyro, accel, mag;
    bno.getCalibration(&sys, &gyro, &accel, &mag);
    if (gyro == 3 && accel == 3) {
      Serial.println("✅ Calibration complete (Gyro & Accel only)!");
      adafruit_bno055_offsets_t newOffsets;
      bno.getSensorOffsets(newOffsets);
      EEPROM.put(1, newOffsets);
      EEPROM.commit();
      Serial.println("💾 Calibration data saved to EEPROM.");

      isCalibrating = false;
      digitalWrite(LED_YELLOW, LOW);
      updateCalibLEDs(gyro, accel);
      delay(5000);
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_BLUE, LOW);
    }
  }
}

String getTimeString() {
  time_t now = millis() / 1000;
  int h = (now / 3600) % 24;
  int m = (now / 60) % 60;
  int s = now % 60;
  char buffer[10];
  sprintf(buffer, "%02d:%02d:%02d", h, m, s);
  return String(buffer);
}

void checkDeepSleepTrigger() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    if (buttonPressStart == 0) buttonPressStart = millis();
    else if (millis() - buttonPressStart > 3000) {
      Serial.println("🔌 Entering Deep Sleep...");
      digitalWrite(LED_PIN, LOW);
      while (digitalRead(BUTTON_PIN) == LOW) delay(10);
      delay(100);
      esp_sleep_enable_ext0_wakeup(GPIO_NUM_14, 0);
      esp_deep_sleep_start();
    }
  } else {
    buttonPressStart = 0;
  }
}

void loop() {
  checkDeepSleepTrigger();
  handleCalibrationButton();
  unsigned long now = millis();

  imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

  if (now - lastSendTime > 100 && WiFi.status() == WL_CONNECTED) {
    String packet = String(boardNumber) + "," + WiFi.localIP().toString() + "," +
                    String(gyro.x(), 3) + "," + String(gyro.y(), 3) + "," + String(gyro.z(), 3) + "," +
                    String(accel.x(), 3) + "," + String(accel.y(), 3) + "," + String(accel.z(), 3);
    udp.beginPacket(raspberry_ip, udp_port);
    udp.print(packet);
    udp.endPacket();
    lastSendTime = now;
  }

  if (now - lastLogTime > 5000) {
    String t = getTimeString();
    Serial.printf("[%s] 📊 Sensor %d | IP: %s | Wi-Fi: %s | Sensor: %s\n",
      t.c_str(), boardNumber, WiFi.localIP().toString().c_str(),
      WiFi.status() == WL_CONNECTED ? "✅" : "❌", sensorReported ? "✅" : "❌");
    Serial.printf("         Gyro X: %.3f   Y: %.3f   Z: %.3f\n", gyro.x(), gyro.y(), gyro.z());
    Serial.printf("         Accel X: %.3f  Y: %.3f  Z: %.3f\n", accel.x(), accel.y(), accel.z());
    lastLogTime = now;
  }
}