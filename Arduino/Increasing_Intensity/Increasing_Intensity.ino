/*
   Tyler Webster
   ESP32 haptic glove firmware
*/

#include <WiFi.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <Wire.h>
#include <Sparkfun_DRV2605L.h>
#include "network_cred.h"

// Toggle Static or Dynamic IP
#define STATIC_IP true
// Set Device ID Used in Static IP
#define DEVICE_ID 4

// Define ADXL345 Accelerometer https://learn.adafruit.com/adxl345-digital-accelerometer/library-reference
const bool ACCEL = true; // Toggle use of accereometer
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(DEVICE_ID); // Using Device ID

// Set Measured Accelerations to Default Value of 0
float accelX = 0;
float accelY = 0;
float accelZ = 0;

// Set network credentials (from network_cred.h)
#define ssid mySSID_0  //wifi SSID
#define password myPASSWORD_0  // wifi Password

// Set port number and define server
int port = 8888;  //Port number
WiFiServer server(port);

// Define Motor Driver and Vibration Signal Bounds
SFE_HMD_DRV2605L HMD;
#define MIN_VIBE 150
#define MAX_VIBE 255

// Motor Pins {ENABLE_PIN, SIGNAL_PWM_PIN}
const int MTR1[2] = {0, 4}; // UP
const int MTR2[2] = {1, 5}; // DOWN
const int MTR3[2] = {2, 6}; // LEFT
const int MTR4[2] = {3, 7}; // RIGHT

// Set All Motors to no Vibration
int val1 = MIN_VIBE;
int val2 = MIN_VIBE;
int val3 = MIN_VIBE;
int val4 = MIN_VIBE;

// On the ESP32S2 SAOLA GPIO 18 is the NeoPixel.
#define LED_PIN 18

// Define NeoPixel RGB LED
Adafruit_NeoPixel pixels(1, LED_PIN, NEO_GRB + NEO_KHZ800);

// Global message holder
String msg;
String outMsg;

// Send signals to a specific motor
void set_motor_output(const int motor_pins[2], int val) {
  // If Vibration Value Below Threshold, Temporarilly Disable Motor
  if (val <= MIN_VIBE) {
    digitalWrite(motor_pins[0], LOW);
    val = MIN_VIBE;
    // Limit Value of Vibration to Max Threshold
  } else if (val > MAX_VIBE) {
    digitalWrite(motor_pins[0], HIGH);
    val = MAX_VIBE;
  } else {
    // Enable Motor
    digitalWrite(motor_pins[0], HIGH);
  }
  // Send Signal to Motor
  analogWrite(motor_pins[1], val);
}

// Read and Decode Messages From TCP Client
void getInput(WiFiClient client) {
  // Message Example /123/456/789/321
  msg = "";

  // If a Message Exists, Read it
  while (client.available() > 0) {
    msg = String(client.readStringUntil('\n'));
    Serial.println(msg);
    if (msg == "accel") {
      Serial.println(outMsg);
      client.println(outMsg);
    } else {
      // Split Message and Assign Values to Motor Signals
      val1 = msg.substring(1, 4).toInt();
      val2 = msg.substring(5, 8).toInt();
      val3 = msg.substring(9, 12).toInt();
      val4 = msg.substring(13, 16).toInt();

      // Send New Signals to each Motor
      set_motor_output(MTR1, val1);
      set_motor_output(MTR2, val2);
      set_motor_output(MTR3, val3);
      set_motor_output(MTR4, val4);
    }

  }
  client.flush();
}

void getAcceleration() {
  sensors_event_t event;
  accel.getEvent(&event);
  accelX = event.acceleration.x;
  accelY = event.acceleration.y;
  accelZ = event.acceleration.z;
  outMsg = String(accelX) + "," + String(accelY) + "," + String(accelZ);
  Serial.print(accelX); Serial.print(","); Serial.print(accelY);
  Serial.print(","); Serial.println(accelY);
}

void setup()
{
  // Enable Serial Output
  Serial.begin(115200);

  // Check if Static IP Address is Needed and Configure Network
  if (STATIC_IP) {
    // Set Static Local IP (This Will Vary by Network Host)
    IPAddress local_IP(172, 16, 1, DEVICE_ID);
    // Set your Gateway IP address (Router's IP)
    IPAddress gateway(172, 16, 1, 1);
    IPAddress subnet(255, 255, 0, 0);

    // Send Serial Message if Configuration Failed
    if (!WiFi.config(local_IP, gateway, subnet)) {
      Serial.println("STA Failed to configure");
    }
  }
  if (ACCEL) {
    //Initialize Accelerometer
    if (!accel.begin())
    {
      /* There was a problem detecting the ADXL345 ... check your connections */
      Serial.println("Ooops, no ADXL345 detected ... Check your wiring!");
      while (1);
    }
    accel.setDataRate(ADXL345_DATARATE_100_HZ);
    accel.setRange(ADXL345_RANGE_16_G);
  }

  // Start Onboard RGB LED
  pixels.setBrightness(5);
  pixels.begin(); // INITIALIZE NeoPixel (REQUIRED)

  // Start Driver Board
  HMD.begin();
  HMD.Mode(0x03); // Set PWM Input Mode
  HMD.MotorSelect(0x0A); // Set Motor Type
  HMD.Library(7); //change to 6 for LRA motors

  // Set All Motor Pins to Outputs
  pinMode(MTR1[0], OUTPUT);
  pinMode(MTR2[0], OUTPUT);
  pinMode(MTR3[0], OUTPUT);
  pinMode(MTR4[0], OUTPUT);
  pinMode(MTR1[1], OUTPUT);
  pinMode(MTR2[1], OUTPUT);
  pinMode(MTR3[1], OUTPUT);
  pinMode(MTR4[1], OUTPUT);

  // Sequentially increase motor intensity starting at min value to max value
  int i = 151;
  while (i < MAX_VIBE){
    set_motor_output(MTR1, i);
    
    set_motor_output(MTR2, i);
    
    set_motor_output(MTR3, i);
    
    set_motor_output(MTR4, i);
    delay(500);
    i += 1;
  }
  set_motor_output(MTR1, MIN_VIBE);
  set_motor_output(MTR2, MIN_VIBE);
  set_motor_output(MTR3, MIN_VIBE);
  set_motor_output(MTR4, MIN_VIBE);

  // Configure Wifi Connection, Start to Connect
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi
  delay(100);

  //RED led before connection
  pixels.setPixelColor(0, Adafruit_NeoPixel::Color(255, 0, 0 ));
  pixels.show();

  // Wait for connection
  Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    delay(500);
  }

  //BLUE led when connected
  pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 0, 255 ));
  pixels.show();


  // Open TCP Server and Print Network Details
  server.begin();
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("on port ");
  Serial.println(port);
}

void loop()
{
  // Execute if WiFi Connected
  if (WiFi.status() == WL_CONNECTED) {
    // Check if a Client has Connected
    WiFiClient client = server.available();

    if (client) {
      if (client.connected())
      {
        // Set LED Green if a Client is Connected
        pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 255, 0 ));
        pixels.show();
        Serial.println("Client Connected");
      }
      // While Client is Connected, Keep Reading Messages From Client
      while (client.connected()) {
        if (ACCEL) {
          getAcceleration();
        }
        getInput(client);

      }

      // Stop Client on Client Disconnect
      client.stop();
      Serial.println("Client disconnected");
      // Turn off motors on client disconnect
      set_motor_output(MTR1, MIN_VIBE);
      set_motor_output(MTR2, MIN_VIBE);
      set_motor_output(MTR3, MIN_VIBE);
      set_motor_output(MTR4, MIN_VIBE);
      // Set LED Back to Blue if Client Disconnected
      pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 0, 255 ));
      pixels.show();
    }
  } else {
    // Set LED to Red if Network Connection Lost
    pixels.setPixelColor(0, Adafruit_NeoPixel::Color(255, 0, 0 ));
    pixels.show();
  }
}
