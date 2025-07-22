// #include <Arduino.h>
// #include <Adafruit_Fingerprint.h>
// #include <WiFi.h>
// #include <AsyncTCP.h>
// #include <SPIFFS.h>
// #include <ESPAsyncWebServer.h>

// AsyncWebServer server(80);
// AsyncEventSource events("/events");

// // WiFi credentials
// const char *ssid = "3ammektaher";
// const char *password = "Destro2204";

// // Fingerprint sensor
// HardwareSerial serialPort(2); // use UART2
// Adafruit_Fingerprint finger = Adafruit_Fingerprint(&serialPort);

// // Relay and buzzer pins
// const int RELAY_PIN = 23;
// const int buzzerPin = 22;

// // Timing variables
// unsigned long previousMillis = 0;
// const long readInterval = 1000;
// bool isOpen = false;
// const long closeInterval = 5000;
// unsigned long previousOpenMillis = 0;

// // Forward declarations
// uint8_t getFingerprintID();
// void showNotAllowed();

// // 404 handler
// void notFound(AsyncWebServerRequest *request) {
//   request->send(404, "text/plain", "Not found");
// }

// void setup() {
//   Serial.begin(9600);
//   while (!Serial) ;
//   delay(100);

//   // Connect to WiFi
//   WiFi.mode(WIFI_STA);
//   WiFi.begin(ssid, password);
//   if (WiFi.waitForConnectResult() != WL_CONNECTED) {
//     Serial.printf("WiFi Failed!\n");
//     return;
//   }
//   Serial.print("IP Address: ");
//   Serial.println(WiFi.localIP());

//   // Initialize SPIFFS
//   if (!SPIFFS.begin(true)) {
//     Serial.println("An Error has occurred while mounting SPIFFS");
//     return;
//   }

//   // Setup Server Sent Events
//   events.onConnect([](AsyncEventSourceClient *client) {
//     if (client->lastId()) {
//       Serial.printf("Client reconnected! Last message ID that it got is: %u\n", client->lastId());
//     }
//   });
//   server.addHandler(&events);

//   // Serve index.html
//   server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
//     Serial.println("Requesting index page...");
//     request->send(SPIFFS, "/index.html", "text/html", false);
//   });
//   server.serveStatic("/css", SPIFFS, "/css/");
//   server.serveStatic("/js", SPIFFS, "/js/");

//   // 404 handler
//   server.onNotFound(notFound);

//   // Start server
//   server.begin();

//   // Fingerprint sensor setup
//   finger.begin(57600);
//   delay(5);
//   if (finger.verifyPassword()) {
//     Serial.println("Found fingerprint sensor!");
//   } else {
//     Serial.println("Did not find fingerprint sensor :(");
//     while (1) { delay(1); }
//   }

//   Serial.println(F("Reading sensor parameters"));
//   finger.getParameters();
//   Serial.print(F("Status: 0x")); Serial.println(finger.status_reg, HEX);
//   Serial.print(F("Sys ID: 0x")); Serial.println(finger.system_id, HEX);
//   Serial.print(F("Capacity: ")); Serial.println(finger.capacity);
//   Serial.print(F("Security level: ")); Serial.println(finger.security_level);
//   Serial.print(F("Device address: ")); Serial.println(finger.device_addr, HEX);
//   Serial.print(F("Packet len: ")); Serial.println(finger.packet_len);
//   Serial.print(F("Baud rate: ")); Serial.println(finger.baud_rate);

//   finger.getTemplateCount();
//   if (finger.templateCount == 0) {
//     Serial.print("Sensor doesn't contain any fingerprint data. Please run the 'enroll' example.");
//   } else {
//     Serial.println("Waiting for valid finger...");
//     Serial.print("Sensor contains ");
//     Serial.print(finger.templateCount);
//     Serial.println(" templates");
//   }

//   // Initialize relay and buzzer
//   pinMode(RELAY_PIN, OUTPUT);
//   digitalWrite(RELAY_PIN, HIGH); // Relay OFF at start
//   pinMode(buzzerPin, OUTPUT);
//   digitalWrite(buzzerPin, LOW);
// }

// void loop() {
//   unsigned long currentMillis = millis();

//   // Close the door lock after 5 seconds
//   if (isOpen && currentMillis - previousOpenMillis >= closeInterval) {
//     isOpen = false;
//     Serial.println("Closing the door lock!");
//     digitalWrite(RELAY_PIN, HIGH);
//     events.send("Door closed", "doorClosed", millis());
//   }

//   // Read fingerprint sensor at interval
//   if (!isOpen && currentMillis - previousMillis >= readInterval) {
//     previousMillis = currentMillis;
//     uint8_t result = getFingerprintID();
//     switch (result) {
//       case FINGERPRINT_NOFINGER:
//         Serial.println("Scan your fingerprint");
//         events.send("Scan your fingerprint", "noFingerprint", millis());
//         break;
//       case FINGERPRINT_OK:
//         Serial.println("Access Granted..opening door lock!");
//         events.send("Access Granted", "accessGranted", millis());
//         previousOpenMillis = millis();
//         isOpen = true;
//         digitalWrite(RELAY_PIN, LOW); // Relay ON (active LOW)
//         break;
//       case FINGERPRINT_NOTFOUND:
//         Serial.println("Access Denied");
//         events.send("Access Denied", "accessDenied", millis());
//         showNotAllowed();
//         delay(2000);
//         break;
//       case FINGERPRINT_PACKETRECIEVEERR:
//       case FINGERPRINT_IMAGEFAIL:
//       case FINGERPRINT_IMAGEMESS:
//       case FINGERPRINT_FEATUREFAIL:
//       case FINGERPRINT_INVALIDIMAGE:
//         Serial.println("Error in Fingerprint Scan!");
//         events.send("Unknown Error", "unknownError", millis());
//         break;
//       default:
//         Serial.println("Unknown Error!");
//         break;
//     }
//   }
// }

// uint8_t getFingerprintID() {
//   uint8_t p = finger.getImage();
//   switch (p) {
//     case FINGERPRINT_OK:
//       Serial.println("Image taken");
//       break;
//     case FINGERPRINT_NOFINGER:
//       return p;
//     case FINGERPRINT_PACKETRECIEVEERR:
//       Serial.println("Communication error");
//       return p;
//     case FINGERPRINT_IMAGEFAIL:
//       Serial.println("Imaging error");
//       return p;
//     default:
//       Serial.println("Unknown error");
//       return p;
//   }

//   // OK success!
//   p = finger.image2Tz();
//   switch (p) {
//     case FINGERPRINT_OK:
//       Serial.println("Image converted");
//       break;
//     case FINGERPRINT_IMAGEMESS:
//       Serial.println("Image too messy");
//       return p;
//     case FINGERPRINT_PACKETRECIEVEERR:
//       Serial.println("Communication error");
//       return p;
//     case FINGERPRINT_FEATUREFAIL:
//       Serial.println("Could not find fingerprint features");
//       return p;
//     case FINGERPRINT_INVALIDIMAGE:
//       Serial.println("Could not find fingerprint features");
//       return p;
//     default:
//       Serial.println("Unknown error");
//       return p;
//   }

//   // OK converted!
//   p = finger.fingerSearch();
//   if (p == FINGERPRINT_OK) {
//     Serial.println("Found a print match!");
//     Serial.print("Found ID #");
//     Serial.print(finger.fingerID);
//     Serial.print(" with confidence of ");
//     Serial.println(finger.confidence);
//     return p;
//   } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
//     Serial.println("Communication error");
//     return p;
//   } else if (p == FINGERPRINT_NOTFOUND) {
//     Serial.println("Did not find a match");
//     return p;
//   } else {
//     Serial.println("Unknown error");
//     return p;
//   }
// }

// void showNotAllowed() {
//   digitalWrite(buzzerPin, HIGH);
//   delay(1000);
//   digitalWrite(buzzerPin, LOW);
// }