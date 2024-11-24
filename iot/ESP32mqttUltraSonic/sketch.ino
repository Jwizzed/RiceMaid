#include <LiquidCrystal_I2C.h>
#include <esp_now.h>
#include <WiFi.h>
#include <PubSubClient.h>

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Ultrasonic sensor pins
#define TRIG_PIN 23
#define ECHO_PIN 19

// WiFi credentials
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT settings
const char* mqtt_server = "iot.cpe.ku.ac.th";
const int mqtt_port = 1883;

// Replace with your MAC Address
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};  // Replace with actual MAC

// Timer variables
unsigned long previousMillis = 0;
const long interval = 5000;  // 5 seconds interval

WiFiClient espClient;
PubSubClient client(espClient);

float duration_us, distance_cm;

// Function to get water level status for rice cultivation
String getWaterLevelStatus(float water_level) {
  if (water_level < 5) {
    return "Critical Low";
  } else if (water_level >= 5 && water_level < 10) {
    return "Low";
  } else if (water_level >= 10 && water_level < 15) {
    return "Optimal";
  } else {
    return "High";
  }
}

void publishDistance() {
  String status = getWaterLevelStatus(distance_cm);
  
  String payload = "{\"device_id\":\"" + WiFi.macAddress() + "\"" +
               ",\"waterlevel\":" + String(distance_cm) +
               ",\"status_waterlevel\":\"" + status + "\"}";
  

  if (client.connected()) {
    client.publish("demo/public/ideathon/distance", payload.c_str());
    Serial.println("Distance and status published to MQTT:");
    Serial.printf("Distance: %.2f cm\n", distance_cm);
    Serial.println("Status: " + status);
    Serial.println("MAC Address: " + WiFi.macAddress());
  } else {
    Serial.println("Client disconnected, couldn't publish");
  }
}

boolean reconnect() {
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);

  if (client.connect(clientId.c_str())) {
    Serial.println("Connected to MQTT Broker!");
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
    Serial.println("MAC address: " + WiFi.macAddress());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void setup() {
  Serial.begin(115200);
  randomSeed(micros());

  // LCD setup
  lcd.init();
  lcd.backlight();

  // Ultrasonic sensor setup
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // WiFi and MQTT setup
  connectToWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  unsigned long currentMillis = millis();

  // Measure distance
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration_us = pulseIn(ECHO_PIN, HIGH);
  distance_cm = 0.017 * duration_us;

  // Get water level status
  String status = getWaterLevelStatus(distance_cm);

  // Update LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Dist: ");
  lcd.print(distance_cm);
  lcd.print("cm");
  lcd.setCursor(0, 1);
  lcd.print("Status: ");
  lcd.print(status);

  // Handle MQTT connection
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

  // Publish distance every 5 seconds when connected
  if (client.connected() && (currentMillis - previousMillis >= interval)) {
    previousMillis = currentMillis;
    publishDistance();
  }

  client.loop();
  delay(500);
}