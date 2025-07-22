#include <Arduino.h>
#include <Adafruit_Fingerprint.h>

// Use UART2 for the fingerprint sensor
HardwareSerial serialPort(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&serialPort);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay(100);

  // Initialize fingerprint sensor
  finger.begin(57600);
  delay(5);
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }

  Serial.println("Attempting to delete all fingerprint templates...");
  int result = finger.emptyDatabase();
  if (result == FINGERPRINT_OK) {
    Serial.println("All fingerprint templates deleted successfully!");
  } else {
    Serial.print("Failed to delete templates. Error code: ");
    Serial.println(result);
  }
}

void loop() {
  // Nothing to do here
} 