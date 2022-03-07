/*
   Copyright (c) 2018, circuits4you.com
   All rights reserved.
   Create a TCP Server on ESP8266 NodeMCU.
   TCP Socket Server Send Receive Demo
*/

#include <WiFi.h>
#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <Sparkfun_DRV2605L.h>

// Define Motor Driver and pins used for pwm signals
SFE_HMD_DRV2605L HMD;

const int Pin0 = 4;
const int Pin1 = 5;
const int Pin2 = 6;
const int Pin3 = 7;

#define MIN_VIBE 150
#define MAX_VIBE 255

int val0 = MIN_VIBE;
int val1 = MIN_VIBE;
int val2 = MIN_VIBE;
int val3 = MIN_VIBE;

#define SendKey 46  //Button to send data Flash BTN on NodeMCU

// On the ESP32S2 SAOLA GPIO is the NeoPixel.
#define PIN        18

//Single NeoPixel
Adafruit_NeoPixel pixels(1, PIN, NEO_GRB + NEO_KHZ800);

int BUZZ = 0;
int BEEP = 5;

//Toggle static or dynamic ip
#define STATIC_IP true


int port = 8888;  //Port number
WiFiServer server(port);

//Server connect to WiFi Network
//const char *ssid = "KrustyKrab2.4";  //Enter your wifi SSID
//const char *password = "Krabbypatties";  //Enter your wifi Password

const char *ssid = "WearablesLab";  //Enter your wifi SSID
const char *password = "";  //Enter your wifi Password

String msg;

void set_motor_output(int en_pin, int pin, int val) {
  if (val <= MIN_VIBE) {
    digitalWrite(en_pin, LOW);
    val = MIN_VIBE;
    digitalWrite(en_pin, LOW);
  } else if (val > MAX_VIBE) {
    digitalWrite(en_pin, HIGH);
    val = MAX_VIBE;
  } else {
    digitalWrite(en_pin, HIGH);
  }
  analogWrite(pin, val);
}


void getInput(WiFiClient client) {
  //Message Example /123/456/789/321
  msg = "";
  while (client.available() > 0) {
    msg = String(client.readStringUntil('\n'));
    Serial.println(msg);

    val0 = msg.substring(1, 4).toInt();
    val1 = msg.substring(5, 8).toInt();
    val2 = msg.substring(9, 12).toInt();
    val3 = msg.substring(13, 16).toInt();

    set_motor_output(0, Pin0, val0);
    set_motor_output(1, Pin1, val1);
    set_motor_output(2, Pin2, val2);
    set_motor_output(3, Pin3, val3);
  }


  client.flush();
}



void setup()
{
  if (STATIC_IP) {
    // Set Static Local IP
    // IPAddress local_IP(172, 16, 1, 2);
    IPAddress local_IP(172, 16, 1, 3);
    // Set your Gateway IP address
    IPAddress gateway(172, 16, 1, 1);
    IPAddress subnet(255, 255, 0, 0);
    if (!WiFi.config(local_IP, gateway, subnet)) {
      Serial.println("STA Failed to configure");
    }
  }


  Serial.begin(115200);

  pixels.setBrightness(5);
  pixels.begin(); // INITIALIZE NeoPixel (REQUIRED)

  // Start Driver Board
  HMD.begin();
  HMD.Mode(0x03); //PWM INPUT
  HMD.MotorSelect(0x0A);
  HMD.Library(7); //change to 6 for LRA motors

  // Set pins to output
  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(Pin0, OUTPUT);
  pinMode(Pin1, OUTPUT);
  pinMode(Pin2, OUTPUT);
  pinMode(Pin3, OUTPUT);

  // Set Driver Board Enable Pins LOW
  digitalWrite(0, LOW);
  digitalWrite(1, LOW);
  digitalWrite(2, LOW);
  digitalWrite(3, LOW);

  analogWrite(Pin0, MIN_VIBE);
  analogWrite(Pin1, MIN_VIBE);
  analogWrite(Pin2, MIN_VIBE);
  analogWrite(Pin3, MIN_VIBE);


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


  // Print Network Details
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
  Serial.print("Open Telnet and connect to IP:");
  Serial.print(WiFi.localIP());
  Serial.print(" on port ");
  Serial.println(port);
}

void loop()
{
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client = server.available();

    if (client) {
      if (client.connected())
      {
        pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 255, 0 ));
        pixels.show();
        Serial.println("Client Connected");
      }

      while (client.connected()) {
        getInput(client);
      }

      /*
        //Send Data to connected client
        while(Serial.available()>0)
        {
        client.write(Serial.read());
        }
      */

      client.stop();
      Serial.println("Client disconnected");
      pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 0, 255 ));
      pixels.show();
    }
  } else {
    pixels.setPixelColor(0, Adafruit_NeoPixel::Color(255, 0, 0 ));
  }
}