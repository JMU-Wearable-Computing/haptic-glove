/*
 * Copyright (c) 2018, circuits4you.com
 * All rights reserved.
 * Create a TCP Server on ESP8266 NodeMCU. 
 * TCP Socket Server Send Receive Demo
*/

#include <WiFi.h>
#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include "Adafruit_DRV2605.h"

Adafruit_DRV2605 drv;

#define SendKey 46  //Button to send data Flash BTN on NodeMCU

// On the ESP32S2 SAOLA GPIO is the NeoPixel.
#define PIN        18 

//Single NeoPixel
Adafruit_NeoPixel pixels(1, PIN, NEO_GRB + NEO_KHZ800);

int BUZZ = 0;
int BEEP = 5;

// Set Static Local IP
IPAddress local_IP(172, 16, 1, 2);
// Set your Gateway IP address
IPAddress gateway(172, 16, 1, 1);
IPAddress subnet(255, 255, 0, 0);

int port = 8888;  //Port number
WiFiServer server(port);

//Server connect to WiFi Network
const char *ssid = "WearablesLab";  //Enter your wifi SSID
const char *password = "";  //Enter your wifi Password

int count=0;
String headers[] = { "buz0", "buz1", "buz2", "buz3" };
String msg;
String key;
int value;

void pulse(int pin, int effect){
  
  digitalWrite(pin, HIGH);
  //delay(duration);
  
  
  // set the effect to play
  drv.setWaveform(0, effect);  // play effect 
  //drv.setWaveform(1, 0);       // end waveform

  // play the effect!
  drv.go();

  // wait a bit
  //delay(500);
  //digitalWrite(pin, LOW);
}

void getInput(WiFiClient client){
  //bool headFound = false;
        msg = "";
        key = "";
        while (client.available() > 0){
        msg = String(client.readStringUntil('\n'));
        key = msg.substring(1, 5);
        value = msg.substring(6, 9).toInt();
        //drv.stop();
        digitalWrite(0, LOW);
        digitalWrite(1, LOW);
        digitalWrite(2, LOW);
        digitalWrite(3, LOW);
        //Serial.print(key); Serial.println(value);
        //pulse(key, value);
        
        if (key.length() > 0){
           if(key == headers[0]){
            pulse(0, value);
          } 
           if(key == headers[1]){
            pulse(1, value);
          }
           if(key == headers[2]){
            pulse(2, value);
          } 
           if(key == headers[3]){
            pulse(3, value);
            //Serial.println("TODO");
          }
        
        //client.print("Message recieved: ");
        //client.print(msg);
        
        }
        client.flush();
      }
}



void setup() 
{
  Serial.begin(115200);

  pixels.setBrightness(5);
  pixels.begin(); // INITIALIZE NeoPixel (REQUIRED)
  
  drv.begin();
  drv.useERM();   
  drv.selectLibrary(1);
  
  // I2C trigger by sending 'go' command 
  // default, internal trigger when sending GO command
  drv.setMode(DRV2605_MODE_INTTRIG);

  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }
  
  pinMode(SendKey,INPUT_PULLUP);  //Btn to send data
  Serial.println();

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
      if(client.connected())
      {
        pixels.setPixelColor(0, Adafruit_NeoPixel::Color(0, 255, 0 ));
        pixels.show();
        Serial.println("Client Connected");
      }
      
      while(client.connected()){  
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
  }else{
    pixels.setPixelColor(0, Adafruit_NeoPixel::Color(255, 0, 0 ));
  }
}
