#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

void setup() {
  Serial.begin(9600);
  ss.begin(GPSBaud);
  Serial.println("{\"status\":\"initializing\"}");
}

void loop() {
  // Feed the GPS object
  while (ss.available() > 0) {
    gps.encode(ss.read());
  }

  // Check if we have a new, valid location fix
  if (gps.location.isUpdated() && gps.location.isValid()) {
    Serial.print("{\"lat\":");
    Serial.print(gps.location.lat(), 6);
    Serial.print(",\"lng\":");
    Serial.print(gps.location.lng(), 6);
    Serial.print(",\"satellites\":");
    Serial.print(gps.satellites.value());
    Serial.println("}");
  }
  
  // Basic error check: If no data after 5 seconds, check wiring
  if (millis() > 5000 && gps.charsProcessed() < 10) {
    // Serial.println("{\"error\":\"No GPS data received, check wiring\"}");
  }
}
