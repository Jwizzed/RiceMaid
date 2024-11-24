#include <esp_now.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// WiFi credentials
const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "iot.cpe.ku.ac.th";
const int mqtt_port = 1883;

// MAC address variable
String MAC_ADDRESS = "";

// Pin definitions
#define SOIL_PIN 34
#define TEMP_PIN 33
#define LED_PIN 12

// Constants
const float BETA = 3950;

// Sensor thresholds
const int SOIL_DRY = 3500;
const int SOIL_WET = 1500;
const float TEMP_HIGH = 30.0;
const float TEMP_LOW = 20.0;

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Timer variables
unsigned long previousMillis = 0;
const long interval = 5000;

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor variables
float temperature;
String soil_status;
int soil_value;
String temp_status;

// Get MAC address as String
String getMacAddress() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char macStr[18] = { 0 };
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(macStr);
}

String getSoilStatus(int value) {
  if (value < SOIL_WET) return "WET";
  if (value > SOIL_DRY) return "DRY";
  return "OK";
}

String getTemperatureStatus(float temp) {
  if (temp > TEMP_HIGH) return "HIGH";
  if (temp < TEMP_LOW) return "LOW";
  return "OK";
}

void readSoilMoisture() {
  soil_value = analogRead(SOIL_PIN);
  int soil_percent = map(soil_value, SOIL_DRY, SOIL_WET, 0, 100);
  soil_percent = constrain(soil_percent, 0, 100);
  soil_status = getSoilStatus(soil_value);
}

void readTemperature() {
  int analogValue = analogRead(TEMP_PIN);
  temperature = 1 / (log(1 / (4095. / analogValue - 1)) / BETA + 1.0 / 298.15) - 273.15;
  temp_status = getTemperatureStatus(temperature);

  if (temperature > TEMP_HIGH) {
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(14, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(14, LOW);
  }
}

void updateLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C ");
  lcd.print(temp_status);

  lcd.setCursor(0, 1);
  lcd.print("Soil:");
  lcd.print(soil_status);
  lcd.print(" ");
  lcd.print(map(soil_value, SOIL_DRY, SOIL_WET, 0, 100));
  lcd.print("%");
}

void publishData() {
  readSoilMoisture();
  readTemperature();
  updateLCD();

  String payload = "{";
  payload += "\"device_id\":\"" + MAC_ADDRESS + "\",";
  payload += "\"temperature\":" + String(temperature, 1) + ",";
  payload += "\"temp_status\":\"" + temp_status + "\",";
  payload += "\"soil_moisture\":" + String(map(soil_value, SOIL_DRY, SOIL_WET, 0, 100)) + ",";
  payload += "\"soil_raw\":" + String(soil_value) + ",";
  payload += "\"soil_status\":\"" + soil_status + "\"";
  payload += "}";

  if (client.connected()) {
    // Using MAC address in MQTT topic
    String topic = "demo/public/ideathon/data";
    client.publish(topic.c_str(), payload.c_str());
    Serial.println("Data published to MQTT:");
    Serial.println("Topic: " + topic);
    Serial.println("Payload: " + payload);
  } else {
    Serial.println("Client disconnected, couldn't publish");
  }
}

boolean reconnect() {
  String clientId = "ESP32--";
  clientId += String(random(0xffff), HEX);

  if (client.connect(clientId.c_str())) {
    Serial.println("Connected to MQTT Broker!");
    // Subscribe to device-specific topic using MAC address
    String topic = "demo/public/ideathon/data";
    client.subscribe(topic.c_str());
    Serial.println("Subscribed to: " + topic);
  }
  return client.connected();
}

void connectToWiFi() {
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.println("IP address: " + WiFi.localIP().toString());
    MAC_ADDRESS = getMacAddress();
    Serial.println("MAC Address: " + MAC_ADDRESS);
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void setup() {
  Serial.begin(115200);
  randomSeed(micros());

  pinMode(LED_PIN, OUTPUT);
  pinMode(SOIL_PIN, INPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(14, OUTPUT);

  Wire.begin(23, 22);
  lcd.init();
  lcd.backlight();

  connectToWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  unsigned long currentMillis = millis();

  if (!client.connected()) {
    Serial.println("Disconnected from MQTT");
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi disconnected, reconnecting...");
      connectToWiFi();
    }

    if (reconnect()) {
      Serial.println("MQTT Reconnected!");
    } else {
      Serial.print("Failed to reconnect to MQTT, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    publishData();
  }

  client.loop();
}