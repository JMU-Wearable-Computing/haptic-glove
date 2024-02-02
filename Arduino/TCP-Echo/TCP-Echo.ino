/*
  Will Bradford
  Echo server script

  Inrements received ASCII character by 1 and sends it via TCP socket
 */

#include <SPI.h> 
#include <WiFiNINA.h>
#include "network_cred.h"
#include "Adafruit_DRV2605.h"

// Mux I2C address
#define TCAADDR 0x70
const bool debug = true;   // Toggle debug mode (Toggle program being verbose)

// Set network credentials (from network_cred.h)
#define ssid mySSID_0
#define password myPASSWORD_0

Adafruit_DRV2605 drv1;

int status = WL_IDLE_STATUS;

WiFiServer server(8888);

// Select which driver to talk to
void muxSelect(uint8_t i) {
  if (i > 7) {
    if (debug) { Serial.println("Invalid mux line selected."); }
    return;
  }
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

// Initialize a driver
void drvInit(Adafruit_DRV2605* driver, int drvNum) {
  muxSelect(drvNum);
  if (!driver->begin()) {
    if (debug) {
      Serial.print("Could not find DRV2605 number ");
      Serial.println(drvNum);
    }
    while (1) delay(10);
  }
  driver->selectLibrary(1);  // Libraries 1-5 are for ERM motors, library 6 is for LRA motors
  driver->setMode(DRV2605_MODE_INTTRIG);
}

// Change the playback effect pattern of the DRV2605 drivers
void changeEffect(Adafruit_DRV2605* driver, int effectNum, int drvNum) {
  muxSelect(drvNum);
  if (effectNum > 0) {  // Set new playback effect
    if (debug) {
      Serial.print("Setting the effect ID of driver ");
      Serial.print(drvNum);
      Serial.print(" to ");
      Serial.println(effectNum);
    }

    if (effectNum > 123) {  // Truncate out-of-bounds numbers to the last available effect (ID# 123)
      effectNum = 123;
    }
    driver->setWaveform(0, effectNum);  // Desired effect
    driver->setWaveform(1, 0);          // End waveform

    if (debug) {
      Serial.print("Effect ID of driver ");
      Serial.print(drvNum);
      Serial.print(" set to ");
      Serial.println(effectNum);
    }
  } else if (effectNum == 0) {  // Stop driver
    if (debug) {
      Serial.print("Stopping driver number ");
      Serial.print(drvNum);
      Serial.println(".");
    }

    driver->stop();

    if (debug) {
      Serial.print("Driver number ");
      Serial.print(drvNum);
      Serial.println(" stopped.");
    }
  } else {  // Do nothing if effectNum < 0
    if (debug) {
      Serial.print("The settings of driver number ");
      Serial.print(drvNum);
      Serial.println(" have not been changed.");
    }
  }
  if (debug) { Serial.println(); }  // Print newline for easier reading
}

// Taken from WiFiNINA example script WiFiWebServer
void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize drivers
  drvInit(&drv1, 1);

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // Don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // Set static local IP (this will vary by network host)
  IPAddress local_IP(172, 16, 1, 4);

  // Set gateway IP address (router's IP)
  IPAddress gateway(172, 16, 1, 1);
  IPAddress dns(172, 16, 1, 1);
  IPAddress subnet(255, 255, 0, 0);

  // Attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);

    // Configurate network
    WiFi.config(local_IP, dns, gateway, subnet);
    status = WiFi.begin(ssid, password);
    delay(100);

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      delay(500);
    }
  }
  server.begin();
  printWifiStatus();
}


void loop() {
  // Listen for incoming clients
  WiFiClient client = server.available();
  if (client) {
    Serial.println("new client");
    while (client.connected()) {
      if (client.available() > 0) {
        
        String oldPacket = String(client.readStringUntil('\n'));
        int msgLength = oldPacket.length() + 1; // + 1 for null terminator
        char msgArray[msgLength];
        oldPacket.toCharArray(msgArray, msgLength);

        Serial.println(msgArray);
        Serial.println();

        //digitalWrite(LED_BUILTIN, HIGH);
        //changeEffect(&drv1, 64, 1);
        //drv1.go();
        //delay(2000);
        //digitalWrite(LED_BUILTIN, LOW);
        //changeEffect(&drv1, 0, 1);
        //drv1.go();

        // Increment received message
        int newASCIIPacket = int(msgArray[0]);
        char newPacket = newASCIIPacket + 1;
        //char newPacket = 'B';
        
        // Send new message
        client.println(newPacket);
      }
    }
    // Close connection
    client.stop();
    Serial.println("client disconnected");
  }
}
