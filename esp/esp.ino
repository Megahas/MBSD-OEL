#include <WiFi.h>
#include <HTTPClient.h>

// Configuration
const char* ssid = "TP-Link_470A";
const char* password = "37475390";
const char* serverUrl = "http://192.168.0.148:5000";

// Button Configuration
const uint8_t buttonPins[3][3] = { // [seat][button]
  {12, 14, 27},  // Seat 1: solo(4), group(2), reset(12)
  {26, 25, 33}, // Seat 2: solo(13), group(14), reset(15)
  {16, 17, 18}  // Seat 3: solo(16), group(17), reset(18)
};

// Button state tracking
uint32_t lastPressTime[3][3] = {0};
bool buttonActive[3][3] = {false};

void setup() {  // <<-- REQUIRED Arduino function
  Serial.begin(115200);
  
  // Configure pins
  for(int seat = 0; seat < 3; seat++) {
    for(int btn = 0; btn < 3; btn++) {
      pinMode(buttonPins[seat][btn], INPUT_PULLUP);
    }
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  for(int i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
  }
  
  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("\nWiFi Failed! Restarting...");
    ESP.restart();
  }
  Serial.println("\nConnected to WiFi");
}

void loop() {  // <<-- REQUIRED Arduino function
  checkAllButtons();
  delay(10); // Small delay to prevent WDT reset
}

void checkAllButtons() {
  const char* statusTypes[3] = {"solo", "group", "empty"};
  
  for(int seat = 0; seat < 3; seat++) {
    for(int btn = 0; btn < 3; btn++) {
      if(digitalRead(buttonPins[seat][btn]) == LOW) {
        if(!buttonActive[seat][btn] && (millis() - lastPressTime[seat][btn] > 300)) {
          buttonActive[seat][btn] = true;
          lastPressTime[seat][btn] = millis();
          
          Serial.printf("Seat %d: %s pressed\n", seat+1, statusTypes[btn]);
          sendToServer(seat+1, statusTypes[btn]);
        }
      } else {
        buttonActive[seat][btn] = false;
      }
    }
  }
}

void sendToServer(uint8_t seat, const char* status) {
  if(WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;
  HTTPClient http;
  
  String url = String(serverUrl) + 
               "/update_status?seat=" + String(seat) + 
               "&status=" + String(status);
  
  http.begin(client, url);
  http.setTimeout(2000);
  
  int httpCode = http.GET();
  if(httpCode == HTTP_CODE_OK) {
    Serial.printf("Seat %d updated to %s\n", seat, status);
  } else {
    Serial.printf("HTTP Error %d\n", httpCode);
  }
  http.end();
}
