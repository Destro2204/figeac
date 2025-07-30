#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <map>
#include <ArduinoJson.h>

// Function prototypes
void enrollFingerprint();
void checkFingerprint();
bool doEnroll(int id);

// WiFi credentials
const char *ssid = "3ammektaher";
const char *password = "Destro2204";

// Flask server (replace with your computer's local IP)
const char *server = "http://10.233.47.51:5050"; // <-- CHANGE THIS

// Fingerprint sensor
HardwareSerial serialPort(2); // use UART2
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&serialPort);

// Relay and buzzer pins
const int RELAY_PIN = 23;
const int buzzerPin = 22;

// For 2 instruments only (overlay2 & overlay3)
const int NUM_INSTRUMENTS = 2;
const int sensorPins[NUM_INSTRUMENTS] = {12, 13};
const int relayPins[NUM_INSTRUMENTS]  = {25, 26};
const int buttonPins[NUM_INSTRUMENTS] = {32, 33};

// Track instrument status
String currentStatus[NUM_INSTRUMENTS] = {"available", "available"};

// Mode: 0 = check, 1 = enroll
int mode = 0;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay(100);

  connectWiFi();

  // Fingerprint sensor setup
  finger.begin(57600);
  delay(5);
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }

  finger.getParameters();
  finger.getTemplateCount();
  Serial.print("Sensor contains ");
  Serial.print(finger.templateCount);
  Serial.println(" templates");

  // Initialize relay and buzzer
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Relay OFF at start
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);

  // Setup for multiple instruments
  for (int i = 0; i < NUM_INSTRUMENTS; i++) {
    pinMode(sensorPins[i], INPUT_PULLUP);   // Adjust as needed
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);       // Locked by default
    pinMode(buttonPins[i], INPUT_PULLUP);   // Adjust as needed
  }

  Serial.println("Type 'e' to enroll, 'c' to check fingerprint.");
}

// Helper: Scan fingerprint and return ID (blocking)
int getFingerprintID() {
  Serial.println("Scan your finger for instrument action...");
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return -1;
  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return -1;
  p = finger.fingerSearch();
  if (p == FINGERPRINT_OK) {
    Serial.print("Found ID #"); Serial.println(finger.fingerID);
    return finger.fingerID;
  } else {
    Serial.println("No match found.");
    digitalWrite(buzzerPin, HIGH);
    delay(1000);
    digitalWrite(buzzerPin, LOW);
    return -1;
  }
}

// Helper: Request access to take instrument
bool requestInstrumentAccess(int fingerprint_ID, int instrument_id) {
  HTTPClient http;
  String url = String(server) + "/api/access-log";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"fingerprint_ID\":" + String(fingerprint_ID) +
                   ",\"status\":\"taken\",\"instrument_id\":" + String(instrument_id) + "}";
  int httpResponseCode = http.POST(payload);
  String response = http.getString();
  Serial.print("Access log response: ");
  Serial.println(response);
  http.end();
  // You can parse response for more logic, but for now, assume 200 = allowed
  return (httpResponseCode == 200);
}

// Helper: Notify server of instrument return
void notifyInstrumentReturn(int fingerprint_ID, int instrument_id) {
  HTTPClient http;
  String url = String(server) + "/api/access-log";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"fingerprint_ID\":" + String(fingerprint_ID) +
                   ",\"status\":\"returned\",\"instrument_id\":" + String(instrument_id) + "}";
  int httpResponseCode = http.POST(payload);
  String response = http.getString();
  Serial.print("Return log response: ");
  Serial.println(response);
  http.end();
}

void loop() {
  // Instrument management logic
  for (int i = 0; i < NUM_INSTRUMENTS; i++) {
    if (digitalRead(buttonPins[i]) == LOW) { // Button pressed
      int fingerprint_ID = getFingerprintID();
      if (fingerprint_ID > 0) { // Only proceed if fingerprint is recognized
        String newStatus = (currentStatus[i] == "available") ? "taken" : "available";

        // 1. Log access
        HTTPClient logHttp;
        String logUrl = String(server) + "/api/access-log";
        logHttp.begin(logUrl);
        logHttp.addHeader("Content-Type", "application/json");
        String logPayload = "{\"fingerprint_ID\":" + String(fingerprint_ID) +
                            ",\"status\":\"" + newStatus + "\",\"instrument_id\":" + String(i+1) + "}";
        int logResponse = logHttp.POST(logPayload);
        logHttp.end();

        // 2. Update instrument status
        HTTPClient http;
        String url = String(server) + "/api/instruments/" + String(i+1);
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        String payload = "{\"status\":\"" + newStatus + "\"}";
        int httpResponseCode = http.PUT(payload);
        Serial.print("PUT /api/instruments/"); Serial.print(i+1);
        Serial.print(" status: "); Serial.println(httpResponseCode);
        Serial.print("Response: "); Serial.println(http.getString());
        http.end();

        // 3. Update local status and provide feedback
        currentStatus[i] = newStatus;
        if (httpResponseCode == 200) {
          // Optionally, unlock/lock relay or provide success feedback
          digitalWrite(relayPins[i], (newStatus == "taken") ? LOW : HIGH);
        }
        delay(500); // Debounce
      } else {
        // Unregistered fingerprint: deny and buzz
        digitalWrite(buzzerPin, HIGH);
        delay(1000);
        digitalWrite(buzzerPin, LOW);
      }
    }
  }

  // Existing mode logic (enroll/check)
  if (Serial.available()) {
    char ch = Serial.read();
    if (ch == 'e') {
      mode = 1;
      Serial.println("Enroll mode. Type 'q' to quit enroll mode.");
    } else if (ch == 'c') {
      mode = 0;
      Serial.println("Check mode");
    }
  }

  if (mode == 1) {
    enrollFingerprint();
  } else if (mode == 0) {
    checkFingerprint();
    delay(1000);
  }

  // Logic for keypad buttons to toggle instrument status
  for (int i = 0; i < NUM_INSTRUMENTS; i++) {
    if (digitalRead(buttonPins[i]) == LOW) { // Button pressed
      int fingerprint_ID = getFingerprintID();
      if (fingerprint_ID > 0) { // Only proceed if fingerprint is recognized
        String newStatus = (currentStatus[i] == "available") ? "taken" : "available";
        HTTPClient http;
        String url = String(server) + "/api/instruments/" + String(i+1);
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        String payload = "{\"status\":\"" + newStatus + "\"}";
        int httpResponseCode = http.PUT(payload);
        Serial.print("PUT /api/instruments/"); Serial.print(i+1);
        Serial.print(" status: "); Serial.println(httpResponseCode);
        Serial.print("Response: "); Serial.println(http.getString());
        http.end();
        currentStatus[i] = newStatus;
        delay(500); // Debounce
      } else {
        // Unregistered fingerprint: deny and buzz
        digitalWrite(buzzerPin, HIGH);
        delay(1000);
        digitalWrite(buzzerPin, LOW);
      }
    }
  }
}

void enrollFingerprint() {
  Serial.println("Enter ID (1-127) for new fingerprint, or 'q' to quit enroll mode:");
  while (true) {
    while (!Serial.available());
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input == "q") {
      mode = 0;
      Serial.println("Exiting enroll mode. Back to check mode.");
      return;
    }
    int id = input.toInt();
    if (id <= 0 || id > 127) {
      Serial.println("Invalid ID. Try again or type 'q' to quit.");
      continue;
    }
    if (!doEnroll(id)) {
      Serial.println("Enroll failed. Try again or type 'q' to quit.");
      continue;
    }
    Serial.println("Enter Employee ID (e.g., EMP001):");
    while (!Serial.available());
    String employeeID = Serial.readStringUntil('\n');
    employeeID.trim();
    Serial.println("Enter Name:");
    while (!Serial.available());
    String name = Serial.readStringUntil('\n');
    name.trim();

    // Register with Flask API
    HTTPClient http;
    String url = String(server) + "/api/employees";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"fingerprint_ID\":" + String(id) + ",\"employee_ID\":\"" + employeeID + "\",\"name\":\"" + name + "\"}";
    int httpResponseCode = http.POST(payload);
    String response = http.getString();
    Serial.print("Registration HTTP code: ");
    Serial.println(httpResponseCode);
    Serial.print("Registration response: ");
    Serial.println(response);
    http.end();

    if (httpResponseCode == 200 || httpResponseCode == 201) {
      Serial.println("Employee registered successfully! You can enroll another or type 'q' to quit.");
    } else {
      Serial.println("Failed to register employee. Try again or type 'q' to quit.");
    }
  }
}

bool doEnroll(int id) {
  int p = -1;
  Serial.print("Waiting for valid finger to enroll as #"); Serial.println(id);
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) continue;
    if (p != FINGERPRINT_OK) { Serial.println("Error, try again."); return false; }
  }
  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) { Serial.println("Image conversion failed."); return false; }
  Serial.println("Remove finger");
  delay(2000);
  while (finger.getImage() != FINGERPRINT_NOFINGER);
  Serial.println("Place same finger again");
  while (finger.getImage() != FINGERPRINT_OK);
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) { Serial.println("Second image conversion failed."); return false; }
  p = finger.createModel();
  if (p != FINGERPRINT_OK) { Serial.println("Model creation failed."); return false; }
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Stored!");
    return true;
  } else {
    Serial.println("Store failed.");
    return false;
  }
}

void checkFingerprint() {
  Serial.println("Scan your finger...");
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return;
  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return;
  p = finger.fingerSearch();
  if (p == FINGERPRINT_OK) {
    Serial.print("Found ID #"); Serial.println(finger.fingerID);
    // Prompt for instrument number
    Serial.println("Enter instrument number (1 or 2):");
    while (!Serial.available());
    int instrument_id = Serial.parseInt();
    Serial.print("Logging access for instrument "); Serial.println(instrument_id);

    // Verify with Flask API
    HTTPClient http;
    String url = String(server) + "/api/verify";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"fingerprint_ID\":" + String(finger.fingerID) + "}";
    int httpResponseCode = http.POST(payload);
    String response = http.getString();
    Serial.print("Verify response: ");
    Serial.println(response);
    http.end();

    if (httpResponseCode == 200) {
      Serial.println("Access Granted! Opening door.");
      digitalWrite(RELAY_PIN, LOW); // Open door
      digitalWrite(buzzerPin, LOW);

      // Notify backend that door is opened
      HTTPClient doorHttp;
      String doorUrl = String(server) + "/api/door-status";
      doorHttp.begin(doorUrl);
      doorHttp.addHeader("Content-Type", "application/json");
      String doorPayload = "{\"status\":\"opened\"}";
      doorHttp.POST(doorPayload);
      doorHttp.end();

      // Fetch current status from backend to determine action
      HTTPClient getHttp;
      String getUrl = String(server) + "/api/instruments";
      getHttp.begin(getUrl);
      int getResponse = getHttp.GET();
      String getPayload = getHttp.getString();
      getHttp.end();
      String newStatus = "taken";
      if (getResponse == 200) {
          DynamicJsonDocument doc(1024);
          DeserializationError error = deserializeJson(doc, getPayload);
          if (!error) {
              for (JsonObject inst : doc.as<JsonArray>()) {
                  if (inst["id"] == instrument_id) {
                      String currentStatus = inst["status"].as<String>();
                      if (currentStatus == "taken") {
                          newStatus = "available";
                      } else {
                          newStatus = "taken";
                      }
                      break;
                  }
              }
          }
      }

      // Log the actual instrument action (taken/available)
      http.begin(String(server) + "/api/access-log");
      http.addHeader("Content-Type", "application/json");
      payload = "{\"fingerprint_ID\":" + String(finger.fingerID) + ",\"status\":\"" + newStatus + "\",\"instrument_id\":" + String(instrument_id) + "}";
      http.POST(payload);
      http.end();

      // Update instrument status
      HTTPClient putHttp;
      String url = String(server) + "/api/instruments/" + String(instrument_id);
      putHttp.begin(url);
      putHttp.addHeader("Content-Type", "application/json");
      String putPayload = "{\"status\":\"" + newStatus + "\"}";
      int putResponse = putHttp.PUT(putPayload);
      Serial.print("PUT /api/instruments/"); Serial.print(instrument_id);
      Serial.print(" status: "); Serial.println(putResponse);
      Serial.print("Response: "); Serial.println(putHttp.getString());
      putHttp.end();

      delay(10000); // Keep door open for 10 seconds
      digitalWrite(RELAY_PIN, HIGH); // Close door
      Serial.println("Door closed.");

      // Notify backend that door is closed
      HTTPClient doorHttp2;
      String doorUrl2 = String(server) + "/api/door-status";
      doorHttp2.begin(doorUrl2);
      doorHttp2.addHeader("Content-Type", "application/json");
      String doorPayload2 = "{\"status\":\"closed\"}";
      doorHttp2.POST(doorPayload2);
      doorHttp2.end();
    } else {
      Serial.println("Access Denied!");
      // Log the access denial
      http.begin(String(server) + "/api/access-log");
      http.addHeader("Content-Type", "application/json");
      payload = "{\"fingerprint_ID\":" + String(finger.fingerID) + ",\"status\":\"failure\",\"instrument_id\":" + String(instrument_id) + "}";
      http.POST(payload);
      http.end();
      
      digitalWrite(buzzerPin, HIGH);
      delay(1000);
      digitalWrite(buzzerPin, LOW);
    }
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("No match found.");
    digitalWrite(buzzerPin, HIGH);
    delay(1000);
    digitalWrite(buzzerPin, LOW);
  }
} 