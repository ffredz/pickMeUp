#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define BUTTON_REGISTER 21  // Physical button to register measurement
#define BUTTON_STORE 22     // Physical button to store measurement


// Wi-Fi credentials
const char* ssid = "Fredrik sin iPhone";
const char* password = "fredrik123";

// Server URL
const char* serverUrlRegister = "http://172.20.10.3:5000/register-measurement";
const char* serverUrlStore = "http://172.20.10.3:5000/store-measurement";

int lastStateRegister = HIGH;
int lastStateStore = HIGH;
float weight = 0.0;

void setup() {
  Serial.begin(115200);
  

  // Set button pins as inputs with pull-up resistors
  pinMode(BUTTON_REGISTER, INPUT_PULLUP);
  pinMode(BUTTON_STORE, INPUT_PULLUP);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Measure distance
  weight = getWeight();
  if (weight > 400 || weight < 2) {
    Serial.println("Out of range");
  } else {
    Serial.print("Weight: ");
    Serial.print(weight, 1);
    Serial.println(" kg");
  }
  
  delay(50);

  // Check if register button was pressed
  int currentStateRegister = digitalRead(BUTTON_REGISTER);
  if (lastStateRegister == HIGH && currentStateRegister == LOW) {
    Serial.println("Register button pressed");
    sendPostRequest(serverUrlRegister, weight);
  }
  lastStateRegister = currentStateRegister;

  // Check if store button was pressed
  int currentStateStore = digitalRead(BUTTON_STORE);
  if (lastStateStore == HIGH && currentStateStore == LOW) {
    Serial.println("Store button pressed");
    sendPostRequest(serverUrlStore, weight);
  }
  lastStateStore = currentStateStore;

  delay(100);
}

float getWeight() {
  int weight;
  weight = random(0,100);
  return weight;
}

void sendPostRequest(const char* url, float weight) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // Create JSON document with the value
    DynamicJsonDocument doc(1024);
    doc["weight"] = weight;

    String jsonData;
    serializeJson(doc, jsonData);

    // Send POST request with JSON data
    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
}
