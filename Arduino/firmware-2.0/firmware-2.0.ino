/*
  Will Bradford
  Haptic Glove 2.0 Firmware

  Message Example: E,100,99,7,54,0,-1,56,46
  Negative numbers will be ignored (use them if you want to keep the current playback effect)
  Passing a 0 or no number will stop the corresponding driver
  Due to C++ magic, message parser behavior is weird when passing values for 4,5, or 6 motors. Pass values for
    all 8 to be safe
  For messages of type 'E', numbers [1, 123] will set the playback effect of the corresponding driver.
    Numbers higher than 123 will set the playback effect to effect # 123
  All decimals will be rounded DOWN
*/

#include "Wire.h"
#include "Adafruit_DRV2605.h"
#include <SPI.h> // This is supposed to be required for WiFiNINA to work but I do not notice a difference in functionality with or without it
#include <WiFiNINA.h>
#include <Arduino_LSM6DS3.h>
#include "network_cred.h"

#define DEVICE_ID 4        // Set device ID used in static IP (Acceptable ranges are 10-100)
#define STATIC_IP true     // Toggle static or dynamic IP
const bool debug = true;   // Toggle debug mode (Toggle program being verbose)
const bool ACCEL = true;  // Toggle use of accelerometer

Adafruit_DRV2605 drv0;
Adafruit_DRV2605 drv1;
Adafruit_DRV2605 drv2;
Adafruit_DRV2605 drv3;
Adafruit_DRV2605 drv4;
/*Adafruit_DRV2605 drv5; // Breadboard does not have functionality for all 8 motors
Adafruit_DRV2605 drv6;
Adafruit_DRV2605 drv7;*/

// Mux I2C address
#define TCAADDR 0x70

// Set network credentials (from network_cred.h)
#define ssid mySSID_0
#define password myPASSWORD_0

// Set Measured Accelerations to Default Value of 0
float accelX = 0;
float accelY = 0;
float accelZ = 0;

// Set port number and define server
int port = 8888;
WiFiServer server(port);

// Stores intensity value of motors
int val0;
int val1;
int val2;
int val3;
int val4;
/*int val5; // Breadboard does not have functionality for all 8 motors
int val6;
int val7;*/

// Global message holder
String packet;
String outMsg;

// Store the supported types of messages; edit as needed
const char msgTypes[] = { 'E' };

// General message structure
struct CommandMessage {
  char cmd;
  int data0;
  int data1;
  int data2;
  int data3;
  int data4;
  int data5;
  int data6;
  int data7;
};

// Instantiate Message object
CommandMessage msgObj;

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

// Test if passed cmd is valid
bool validateCmd(char cmd) {
  for (char letter : msgTypes) {
    if (letter == cmd) {
      return true;
    }
  }
  return false;
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

    driver->go();
  }
  else if (effectNum == 0) {  // Stop driver
    if (debug) {
      Serial.print("Stopping driver number ");
      Serial.print(drvNum);
      Serial.println(".");
    }

    //driver->setWaveform(0, effectNum);  // Desired effect
    //driver->setWaveform(1, 0);          // End waveform

    driver->stop();

    if (debug) {
      Serial.print("Driver number ");
      Serial.print(drvNum);
      Serial.println(" stopped.");
    }
  }
  else {  // Repeat effect if effectNum < 0
    if (debug) {
      Serial.print("The settings of driver number ");
      Serial.print(drvNum);
      Serial.println(" have not been changed.");
    }

    driver->go();
  }
  if (debug) { Serial.println(); }  // Print newline for easier reading
}

// Parse received packet
void createCmdMsg(String* packetPtr) {
  if (debug) {
    Serial.print("\nMessage reads "); Serial.println(*packetPtr);
  }

  if (*packetPtr == "accel") {
    Serial.println(outMsg);
    Serial.println(outMsg);
  }
  else {  // Split message and assign values to Motor Signals
    // Make msg into an array
    int msgLength;

    if (packetPtr->length() < 9) {  // Allows for user to pass messages that are < the number of parameters needed to create a Message object
      if (debug) {
        Serial.print("Message length is "); Serial.print(packetPtr->length()); Serial.println(", but it was forced to be 9.");
      }
      msgLength = 9;
    } else {
      msgLength = packetPtr->length() + 1;  // Add 1 character for null terminator

      if (debug) {
        Serial.print("Message length is ");
        Serial.println(msgLength);
      }
    }

    char msgArray[msgLength];                     // Create array
    packetPtr->toCharArray(msgArray, msgLength);  // Copy msg to previously created array

    /*

        strtok() has state and remembers the delimeter. Be carefel thar be dragons!!!!!!!!

    */

    char* msgPieces[msgLength];  // An array of pointers to the pieces of msg after strtok()
    char* ptr = NULL;

    byte index = 0;
    ptr = strtok(msgArray, ",");  // Delimiter
    while (ptr != NULL) {         // Parse the message and place pieces into array
      msgPieces[index] = ptr;
      index++;
      ptr = strtok(NULL, ",");
    }
    /*for (int n = index; n < 8; n++) {
      msgPieces[n] = 0;
      index++;
    }*/

    if (debug) {
      Serial.println("The message pieces detected are:");
      for (int n = 0; n < index; n++) {
        Serial.print(n); Serial.print("  "); Serial.println(msgPieces[n]);
      }
      Serial.println();  // Print newline for easier reading
    }

    /*

      Parity check goes here (?)
      Checksum is a single for loop in its implementation
    
    */

    // Test if valid cmd
    if (validateCmd(*msgPieces[0])) {

      if (debug) {Serial.println("Command validated"); Serial.println("Created a message object with the following parameters:");}

      // Create Message object
      msgObj.cmd = *msgPieces[0];
      if (debug) {Serial.print("msgObj.cmd = "); Serial.println(msgObj.cmd);}
      msgObj.data0 = atoi(msgPieces[1]);
      if (debug) {Serial.print("msgObj.data0 = "); Serial.println(msgObj.data0);}
      msgObj.data1 = atoi(msgPieces[2]);
      if (debug) {Serial.print("msgObj.data1 = "); Serial.println(msgObj.data1);}
      msgObj.data2 = atoi(msgPieces[3]);
      if (debug) {Serial.print("msgObj.data2 = "); Serial.println(msgObj.data2);}
      msgObj.data3 = atoi(msgPieces[4]);
      if (debug) {Serial.print("msgObj.data3 = "); Serial.println(msgObj.data3);}
      msgObj.data4 = atoi(msgPieces[5]);
      if (debug) {Serial.print("msgObj.data4 = "); Serial.println(msgObj.data4);}
      msgObj.data5 = atoi(msgPieces[6]);
      if (debug) {Serial.print("msgObj.data5 = "); Serial.println(msgObj.data5);}
      msgObj.data6 = atoi(msgPieces[7]);
      if (debug) {Serial.print("msgObj.data6 = "); Serial.println(msgObj.data6);}
      msgObj.data7 = atoi(msgPieces[8]);
      if (debug) {Serial.print("msgObj.data7 = "); Serial.println(msgObj.data7); Serial.println();}

      /*if (debug) {
        Serial.println("Created a message object with the following parameters:");
        Serial.print("msgObj.cmd = ");
        Serial.println(msgObj.cmd);
        Serial.print("msgObj.data0 = ");
        Serial.println(msgObj.data0);
        Serial.print("msgObj.data1 = ");
        Serial.println(msgObj.data1);
        Serial.print("msgObj.data2 = ");
        Serial.println(msgObj.data2);
        Serial.print("msgObj.data3 = ");
        Serial.println(msgObj.data3);
        Serial.print("msgObj.data4 = ");
        Serial.println(msgObj.data4);
        Serial.print("msgObj.data5 = ");
        Serial.println(msgObj.data5);
        Serial.print("msgObj.data6 = ");
        Serial.println(msgObj.data6);
        Serial.print("msgObj.data7 = ");
        Serial.println(msgObj.data7);
        Serial.println();
      }*/
    }
    else {  // Handle invalid cmd letters; retry input
      if (debug) { Serial.println("Invalid Message type received."); }
    }
  }
}

// Process Message object as an eMessage
void processEMessage(CommandMessage* msgToSend) {
  if (debug) { Serial.println("Processing as an effect message."); }

  // Assign effect numbers
  val0 = msgToSend->data0;
  val1 = msgToSend->data1;
  val2 = msgToSend->data2;
  val3 = msgToSend->data3;
  val4 = msgToSend->data4;
  /*val5 = msgToSend->data5; // Breadboard does not have functionality for all 8 motors
  val6 = msgToSend->data6;
  val7 = msgToSend->data7;*/

  if (debug) {
    Serial.print("val0 = ");
    Serial.println(val0);
    Serial.print("val1 = ");
    Serial.println(val1);
    Serial.print("val2 = ");
    Serial.println(val2);
    Serial.print("val3 = ");
    Serial.println(val3);
    Serial.print("val4 = ");
    Serial.println(val4);
    /*Serial.print("val5 = "); Serial.println(val5); // Breadboard does not have functionality for all 8 motors
    Serial.print("val6 = "); Serial.println(val6);
    Serial.print("val7 = "); Serial.println(val7);*/
    Serial.println();  // Print newline for easier reading
  }

  // Send new signals to each motor
  /*changeEffect(&drv0, val0, 0);
  changeEffect(&drv1, val1, 1);
  changeEffect(&drv2, val2, 2);
  changeEffect(&drv3, val3, 3);
  changeEffect(&drv4, val4, 4);*/
  /*changeEffect(&drv5, val5, 5); // Breadboard does not have functionality for all 8 motors
  changeEffect(&drv6, val6, 6);
  changeEffect(&drv7, val7, 7);*/

  if (debug) { Serial.println("\n"); }  // Print 2 newlines for easier reading
}

void getAcceleration() {
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(accelX, accelY, accelZ);
  }
  outMsg = String(accelX) + "," + String(accelY) + "," + String(accelZ);
  if (debug) {
    Serial.println("\nAcceleration in G's");
    Serial.println("X\tY\tZ");
    Serial.print(accelX);
    Serial.print('\t');
    Serial.print(accelY);
    Serial.print('\t');
    Serial.println(accelZ);
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize drivers
  drvInit(&drv0, 0);
  drvInit(&drv1, 1);
  drvInit(&drv2, 2);
  drvInit(&drv3, 3);
  drvInit(&drv4, 4);
  /*drvInit(&drv5, 5); // Breadboard does not have functionality for all 8 motors
  drvInit(&drv6, 6);
  drvInit(&drv7, 7);*/

  // Sequentially activate/deactivate drivers
  if (debug) { Serial.println("Cycling drivers"); }
  changeEffect(&drv0, 64, 0);
  drv0.go();
  delay(500);
  changeEffect(&drv1, 64, 1);
  drv1.go();
  delay(500);
  changeEffect(&drv2, 64, 2);
  drv2.go();
  delay(500);
  changeEffect(&drv3, 64, 3);
  drv3.go();
  delay(500);
  changeEffect(&drv4, 64, 4);
  drv4.go();
  /*delay(500);
  changeEffect(&drv5, 64, 5); // Breadboard does not have functionality for all 8 motors
  drv5.go();
  delay(500);
  changeEffect(&drv6, 64, 6);
  drv6.go();
  delay(500);
  changeEffect(&drv7, 64, 7);
  drv7.go();*/
  if (debug) { Serial.println("Drivers cycled\n"); }

  // Check if static IP address is needed and configure network
  if (STATIC_IP) {
  // Set static local IP (this will vary by network host)
  IPAddress local_IP(172, 16, 1, DEVICE_ID);

  // Set gateway IP address (router's IP)
  IPAddress gateway(172, 16, 1, 1);
  IPAddress dns(172, 16, 1, 1);
  IPAddress subnet(255, 255, 0, 0);
    if (debug) {
      Serial.print("Local IP address set to: ");
      Serial.println(local_IP);
      Serial.print("Gateway set to: ");
      Serial.println(gateway);
      Serial.print("DNS set to: ");
      Serial.println(dns);
      Serial.print("Subnet set to: ");
      Serial.println(subnet);
      Serial.println();
    }

    // Configurate network
    WiFi.config(local_IP, dns, gateway, subnet);
  }
  if (ACCEL) {
    // Initialize accelerometer
    if (!IMU.begin()) {
      if (debug) { Serial.println("Failed to initialize IMU!"); }

      while (1)
        ;
    }
    if (debug) {
      Serial.println("Accelerometer initialized");
      Serial.print("Sample rate = ");
      Serial.print(IMU.accelerationSampleRate());
      Serial.println(" Hz\n");
    }
  }

  // Configure WiFi connection, start to connect
  WiFi.begin(ssid, password);  // Connect to WiFi
  delay(100);                  // Is this needed?

  // Wait for connection
  if (debug) { Serial.println("Connecting to WiFi"); }
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (debug) { Serial.print("."); }
    delay(500);
  }

  // blink LED when connected to WiFi

  // Open TCP server
  server.begin();
  if (debug) {  // Print network details
    Serial.print("\nConnected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("on port ");
    Serial.println(port);
  }
}

void loop() {

  //                                            *** Via WiFi ***

  // Execute if WiFi connected
  if (WiFi.status() == WL_CONNECTED) {
    // Check if a client has connected
    WiFiClient client = server.available();

    if (client) {
      if (client.connected()) {
        // LED on if client connected
        digitalWrite(LED_BUILTIN, HIGH);
        if (debug) { Serial.println("Client connected"); }
      }
      // While client is connected, keep reading messages from client
      while (client.connected()) {
        if (ACCEL) {
          getAcceleration();
        }
        // If a message exists, read it
        if (client.available() > 0) {
          packet = String(client.readStringUntil('\n'));
          if (packet == "accel") {
            if (debug) {
              Serial.print("outMsg = ");
              Serial.println(outMsg);
            }
            client.println(outMsg);
          }
          else {
            createCmdMsg(&packet);
            if (msgObj.cmd == 'E') {  // Process as effect message; Explicitly check for equality to prepare for additional command letters being integrated in the future
              processEMessage(&msgObj);
            }
          }
        }
        // Send new signals to each motor
        changeEffect(&drv0, val0, 0);
        changeEffect(&drv1, val1, 1);
        changeEffect(&drv2, val2, 2);
        changeEffect(&drv3, val3, 3);
        changeEffect(&drv4, val4, 4);
        /*changeEffect(&drv5, val5, 5); // Breadboard does not have functionality for all 8 motors
        changeEffect(&drv6, val6, 6);
        changeEffect(&drv7, val7, 7);*/
        client.flush();
      }

      // Stop client on client disconnect
      client.stop();
      if (debug) { Serial.println("Client disconnected\n"); }

      // Turn off motors on client disconnect
      val0 = 0;
      changeEffect(&drv0, 0, 0);
      val1 = 0;
      changeEffect(&drv1, 0, 1);
      val2 = 0;
      changeEffect(&drv2, 0, 2);
      val3 = 0;
      changeEffect(&drv3, 0, 3);
      val4 = 0;
      changeEffect(&drv4, 0, 4);
      /*changeEffect(&drv5, 0, 5); // Breadboard does not have functionality for all 8 motors
      changeEffect(&drv6, 0, 6);
      changeEffect(&drv7, 0, 7);*/

      // TODO: Make LED blink when connected to WiFi but not client. Currently just turns off
      digitalWrite(LED_BUILTIN, LOW);
    }
  } else {
    // LED off if connection lost
    if (debug) { Serial.println("Network connection lost"); }
    digitalWrite(LED_BUILTIN, LOW);
  }

  //                                            *** Via Serial ***

  // If a message exists, read it
  if (Serial.available() > 0) {
    if (ACCEL) {
      getAcceleration();
    }
    packet = String(Serial.readStringUntil('\n'));
    if (packet == "accel") {
      if (debug) {
        Serial.print("outMsg = ");
        Serial.println(outMsg);
      }
    } else {
      createCmdMsg(&packet);
      if (msgObj.cmd == 'E') {  // Process as effect message; Explicitly check for equality to prepare for additional command letters being integrated in the future
        processEMessage(&msgObj);

        // Send new signals to each motor
        changeEffect(&drv0, val0, 0);
        changeEffect(&drv1, val1, 1);
        changeEffect(&drv2, val2, 2);
        changeEffect(&drv3, val3, 3);
        changeEffect(&drv4, val4, 4);
        /*changeEffect(&drv5, val5, 5); // Breadboard does not have functionality for all 8 motors
        changeEffect(&drv6, val6, 6);
        changeEffect(&drv7, val7, 7);*/
      }
    }
  }
  Serial.flush(); // Is this needed? "Waits for the transmission of outgoing serial data to complete"

  // Continuously play effects after message receival
  if (val0 != 0) {
    muxSelect(0);
    drv0.go();
  }
  if (val1 != 0) {
    muxSelect(1);
    drv1.go();
  }
  if (val2 != 0) {
    muxSelect(2);
    drv2.go();
  }
  if (val3 != 0) {
    muxSelect(3);
    drv3.go();
  }
  if (val4 != 0) {
    muxSelect(4);
    drv4.go();
  }
  /*if (val5 != 0) { // Breadboard does not have functionality for all 8 motors
    muxSelect(5);
    drv5.go();
  }
  if (val6 != 0) {
    muxSelect(6);
    drv6.go();
  }
  if (val7 != 0) {
    muxSelect(7);
    drv7.go();
  }*/
}
