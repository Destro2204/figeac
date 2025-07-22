#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Function prototypes
void enrollFingerprint();
void checkFingerprint();
bool doEnroll(int id);

// WiFi credentials
const char *ssid = "3ammektaher";
const char *password = "Destro2204";

// Flask server (replace with your computer's local IP)
const char *server = "http://10.253.219.50:5050"; // <-- CHANGE THIS

// Fingerprint sensor
HardwareSerial serialPort(2); // use UART2
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&serialPort);

// Relay and buzzer pins
const int RELAY_PIN = 23;
const int buzzerPin = 22;

// For 3 instruments
const int NUM_INSTRUMENTS = 2;
const int sensorPins[NUM_INSTRUMENTS] = {12, 13};   // Only 2 sensors
const int relayPins[NUM_INSTRUMENTS]  = {25, 26};
const int buttonPins[NUM_INSTRUMENTS] = {32, 33};

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
    // Button pressed (active LOW)
    if (digitalRead(buttonPins[i]) == LOW) {
      Serial.print("Button pressed for instrument "); Serial.println(i+1);
      int fingerprint_ID = getFingerprintID();
      if (fingerprint_ID > 0) {
        if (requestInstrumentAccess(fingerprint_ID, i+1)) { // instrument_id = i+1
          digitalWrite(relayPins[i], LOW); // Unlock relay
          Serial.println("Instrument unlocked.");
          delay(1000); // Debounce
        } else {
          Serial.println("Access denied for this instrument.");
          digitalWrite(buzzerPin, HIGH);
          delay(1000);
          digitalWrite(buzzerPin, LOW);
        }
      }
    }
    // Instrument returned (sensor active LOW)
    if (digitalRead(sensorPins[i]) == LOW) {
      Serial.print("Instrument "); Serial.print(i+1); Serial.println(" returned.");
      int fingerprint_ID = getFingerprintID();
      if (fingerprint_ID > 0) {
        notifyInstrumentReturn(fingerprint_ID, i+1);
        digitalWrite(relayPins[i], HIGH); // Lock relay
        delay(1000); // Debounce
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

    // Log access attempt
    http.begin(String(server) + "/api/access-log");
    http.addHeader("Content-Type", "application/json");
    String status = (httpResponseCode == 200) ? "success" : "failure";
    payload = "{\"fingerprint_ID\":" + String(finger.fingerID) + ",\"status\":\"" + status + "\"}";
    http.POST(payload);
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