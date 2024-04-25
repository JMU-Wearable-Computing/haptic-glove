/*
  Will Bradford
  Haptic Glove V2 Firmware

  Due to C++ magic, message parser behavior is weird when passing values for less than 8 motors. Pass values for
    all 8 to be safe
*/

#include "Wire.h"
#include "Adafruit_DRV2605.h"
#include "math.h"
#include <SPI.h> // This is supposed to be required for WiFiNINA to work but I do not notice a difference in functionality with or without it
#include <WiFiNINA.h>
#include <Arduino_LSM6DS3.h>
#include "network_cred.h"

// User definable variables
#define DEVICE_ID 10             // Set device ID used in static IP (Acceptable ranges are 10-100)
#define STATIC_IP true           // Toggle static or dynamic IP
const bool debug = true;         // Toggle debug mode (Toggle program being verbose)
int port = 8888;                 // Port number for WiFi server

// This toggles whether or not to activate the eighth driver for use. Only toggle this if:
// (A) you want to only use transmit messages Serially, or
// (B) you're a pro user and want to try to fix things
const bool theDastardlyEighthDriver = false;

// Do not change
#define MUXRST 17                // Mux Reset pin is tied to Arudino pin D17 for on-demand resets
#define MUXADDR 0x70             // Mux I2C address
#define ssid mySSID_0            // Network SSID (from network_cred.h)
#define password myPASSWORD_0    // Network password (from network_cred.h)
// const uint8_t MAGIC_BYTE = 0xff; // Magic byte used for checksum (Currently unused)

// Motor driver objects
Adafruit_DRV2605 drv0;
Adafruit_DRV2605 drv1;
Adafruit_DRV2605 drv2;
Adafruit_DRV2605 drv3;
Adafruit_DRV2605 drv4;
Adafruit_DRV2605 drv5;
Adafruit_DRV2605 drv6;
Adafruit_DRV2605 drv7;

// Set Measured Accelerations to Default Value of 0
float accelX = 0;
float accelY = 0;
float accelZ = 0;
float mag = 0;
bool accelToggle = false; // Toggle for continual transmission of accel data

// Define server, set static local IP (this will vary by network host)
// TODO: Add instructions on what parts of these things to change to allow the user to connect to their own network. Move to above in the user definable variables
WiFiServer server(port);
IPAddress local_IP(172, 16, 1, DEVICE_ID);

// Set gateway IP address (router's IP)
IPAddress gateway(172, 16, 1, 1);
IPAddress dns(172, 16, 1, 1);
IPAddress subnet(255, 255, 0, 0);

// Stores intensity value of motors
int val0;
int val1;
int val2;
int val3;
int val4;
int val5;
int val6;
int val7;

// Global message holder
String packet;
String outMsg;

// Store the supported types of messages; edit as needed
const char msgTypes[] = { 'E', 'A' };

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

// Connect to WiFi
void WiFiConnect() {
  // Check if static IP address is needed and configure network
  if (STATIC_IP) {
    WiFi.config(local_IP, dns, gateway, subnet);
    if (debug) {
      Serial.print("Local IP address set to: "); Serial.println(local_IP);
      Serial.print("Gateway set to: "); Serial.println(gateway);
      Serial.print("DNS set to: "); Serial.println(dns);
      Serial.print("Subnet set to: "); Serial.println(subnet);
      Serial.println();
    }
  }

  // Configure WiFi connection, start to connect
  WiFi.begin(ssid, password);  // Connect to WiFi
  delay(100);                  // Is this needed?

  // Wait for connection
  if (debug) { Serial.println("Connecting to WiFi..."); }
  while (WiFi.status() != WL_CONNECTED) {
    if (debug) { Serial.print("."); }
    delay(500);
  }

  // TODO: blink LED when connected to WiFi

  // Open TCP server
  server.begin();
  if (debug) {  // Print network details
    Serial.print("\nConnected to "); Serial.println(ssid);
    Serial.print("IP address: "); Serial.println(WiFi.localIP());
    Serial.print("on port "); Serial.println(port);
  }
  // TODO: LED blinking if connected to WiFi but not client. Currently is just on
  digitalWrite(LED_BUILTIN, HIGH);
}

// Select which driver to talk to
void muxSelect(uint8_t i) {
  if (i > 7) {
    if (debug) { Serial.println("Invalid mux line selected."); }
    return;
  }
  Wire.beginTransmission(MUXADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

// Initialize a driver
void drvInit(Adafruit_DRV2605* driver, int drvNum) {
  if (debug) {Serial.print("Initializing driver "); Serial.println(drvNum);}
  
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

  if (debug) {Serial.print("Driver "); Serial.print(drvNum); Serial.println(" initialized.");}
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

  // Split message and assign values to Motor Signals
  // Make msg into an array
  int msgLength;

  if (packetPtr->length() < 9) {  // Allows for user to pass messages that are < the number of parameters needed to create a Message object
    if (debug) {
      Serial.print("Message length is "); Serial.print(packetPtr->length()); Serial.println(", but it was forced to be 9.");
    }
    msgLength = 9;
  }
  else {
    msgLength = packetPtr->length() + 1;  // Add 1 character for null terminator

    if (debug) {
      Serial.print("Message length is ");
      Serial.println(msgLength);
    }
  }

  char msgArray[msgLength];                     // Create array
  packetPtr->toCharArray(msgArray, msgLength);  // Copy msg to previously created array

  /*
    **************************************************************************************************************
      strtok() has state and remembers the delimeter. Be carefel thar be dragons!!!!!!!!
    **************************************************************************************************************
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

  if (debug) {
    Serial.println("The message pieces detected are:");
    for (int n = 0; n < index; n++) {
      Serial.print(n); Serial.print("  "); Serial.println(msgPieces[n]);
    }
    Serial.println();  // Print newline for easier reading
  }

  // Test if valid cmd
  if (validateCmd(*msgPieces[0])) {

    if (debug) {Serial.println("Command validated"); Serial.println("Created a message object with the following parameters:");}

    // Create Message object; ignore checksum at the end
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
    if (theDastardlyEighthDriver) {
      msgObj.data7 = atoi(msgPieces[8]);
      if (debug) {Serial.print("msgObj.data7 = "); Serial.println(msgObj.data7); Serial.println();}
    }
  }
  else {  // Handle invalid cmd letters; retry input
    if (debug) { Serial.println("Invalid Message type received."); }
  }
}

// Process Message object as an eMessage
void processEMessage(CommandMessage* msgToSend) {
  if (debug) { Serial.println("Processing as an effect message."); }

  // Assign effect numbers
  val0 = msgToSend->data0;
  if (debug) {Serial.print("val0 = "); Serial.println(val0);}
  val1 = msgToSend->data1;
  if (debug) {Serial.print("val1 = "); Serial.println(val1);}
  val2 = msgToSend->data2;
  if (debug) {Serial.print("val2 = "); Serial.println(val2);}
  val3 = msgToSend->data3;
  if (debug) {Serial.print("val3 = "); Serial.println(val3);}
  val4 = msgToSend->data4;
  if (debug) {Serial.print("val4 = "); Serial.println(val4);}
  val5 = msgToSend->data5;
  if (debug) {Serial.print("val5 = "); Serial.println(val5);}
  val6 = msgToSend->data6;
  if (debug) {Serial.print("val6 = "); Serial.println(val6);}
  if (theDastardlyEighthDriver) {
    val7 = msgToSend->data7;
    if (debug) {Serial.print("val7 = "); Serial.println(val7); Serial.println();}
  }

  if (debug) { Serial.println("\n"); }  // Print 2 newlines for easier reading
}

// Process Message object as an aMessage
void getAcceleration() {
  if (IMU.accelerationAvailable()) { // If there is new acceleration data available

    // Measure acceleration data
    IMU.readAcceleration(accelX, accelY, accelZ);

    // Calculate magnitude
    mag = sqrt(pow(accelX, 2) + pow(accelY, 2) + pow(accelZ, 2));

    // Update message to send
    outMsg = String(accelX) + "," + String(accelY) + "," + String(accelZ) + "," + String(mag);
    if (debug) {
      Serial.println("\nAcceleration in G's");
      Serial.println("X\tY\tZ\tMag");
      Serial.print(accelX); Serial.print('\t'); Serial.print(accelY);
      Serial.print('\t'); Serial.print(accelZ); Serial.print('\t'); Serial.println(mag);

      Serial.print("outMsg = "); Serial.println(outMsg);
    }
    // Wait for new acceleration data to populate
    // TODO: Is it beneficial to have a dedicated global variable that stores the accelerometer's sample rate?
    delay((1 / IMU.accelerationSampleRate()) * 1000); // Comment out if sample rate is low so that this doesn't delay new messages from being read
  }
  else {
    if (debug) {Serial.println("ERROR: Failed to read acceleration");}
  }
}

void serialDrvCtrl() {
  // If a message exists, read it
  if (Serial.available() > 0) {
    packet = String(Serial.readStringUntil('\n'));
    createCmdMsg(&packet);
    if (msgObj.cmd == 'E') {  // Process as effect message
      processEMessage(&msgObj);

      // Send new signals to each motor
      changeEffect(&drv0, val0, 0);
      changeEffect(&drv1, val1, 1);
      changeEffect(&drv2, val2, 2);
      changeEffect(&drv3, val3, 3);
      changeEffect(&drv4, val4, 4);
      changeEffect(&drv5, val5, 5);
      changeEffect(&drv6, val6, 6);
      if (theDastardlyEighthDriver) {changeEffect(&drv7, val7, 7);}
    }
    else if (msgObj.cmd == 'A') { // Process as acceleration message
      if (msgObj.data0 == 0) { // Stop polling accelerometer
        accelToggle = false;
        if (debug) {Serial.println("\nAccelerometer stopped");}
      }
      else {
        accelToggle = true;
      }
    }
  }
}

// Stop all motor drivers
void allDrvStop() {
  val0 = 0;
  changeEffect(&drv0, val0, 0);
  val1 = 0;
  changeEffect(&drv1, val1, 1);
  val2 = 0;
  changeEffect(&drv2, val2, 2);
  val3 = 0;
  changeEffect(&drv3, val3, 3);
  val4 = 0;
  changeEffect(&drv4, val4, 4);
  val5 = 0;
  changeEffect(&drv5, val5, 5);
  val6 = 0;
  changeEffect(&drv6, val6, 6);
  if (theDastardlyEighthDriver) {
    val7 = 0;
    changeEffect(&drv7, val7, 7);
  }
}

// Play current effect on all drivers
void allDrvPlay() {
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
  if (val5 != 0) {
    muxSelect(5);
    drv5.go();
  }
  if (val6 != 0) {
    muxSelect(6);
    drv6.go();
  }
  if (theDastardlyEighthDriver) {
    if (val7 != 0) {
      muxSelect(7);
      drv7.go();
    }
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  pinMode(LED_BUILTIN, OUTPUT);

  // Tie mux RST high
  pinMode(MUXRST, OUTPUT);
  digitalWrite(MUXRST, HIGH);

  // Initialize drivers
  drvInit(&drv0, 0);
  drvInit(&drv1, 1);
  drvInit(&drv2, 2);
  drvInit(&drv3, 3);
  drvInit(&drv4, 4);
  drvInit(&drv5, 5);
  drvInit(&drv6, 6);
  if (theDastardlyEighthDriver) {drvInit(&drv7, 7);}

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
  delay(500);
  changeEffect(&drv5, 64, 5);
  drv5.go();
  delay(500);
  changeEffect(&drv6, 64, 6);
  drv6.go();
  if (theDastardlyEighthDriver) {
    delay(500);
    changeEffect(&drv7, 64, 7);
    drv7.go();
  }
  if (debug) { Serial.println("Drivers cycled\n"); }

  // Connect to WiFi
  WiFiConnect();

  // Initialize accelerometer
  if (!IMU.begin()) {
    if (debug) { Serial.println("Failed to initialize IMU!"); }

    while (1)
      ;
  }
  if (debug) {
    Serial.println("\nAccelerometer initialized");
    Serial.print("Sample rate = "); Serial.print(IMU.accelerationSampleRate()); Serial.println(" Hz\n");
  }

  if (debug) {Serial.println("System ready for use!");}
}

void loop() {

  //********************************************** Control Via WiFi **********************************************

  // Execute if WiFi connected
  if (WiFi.status() == WL_CONNECTED) {
    // Check if a client has connected
    WiFiClient client = server.available();

    // TODO: LED blinking if connected to WiFi but not client. Currently is just on
    if (client) { // This evaluates as 0 unless a message has appeared over the TCP socket
      if (client.connected()) {
        // TODO: LED on if client connected. Currently is on if connected to WiFi
        if (debug) { Serial.println("Client connected"); }
      }
      // While client is connected, keep reading messages from client
      while (client.connected()) {
        // If a message exists, read it
        if (client.available() > 0) {
          packet = String(client.readStringUntil('\n')); // TODO: turn packet into a char array from inception to simplify later code in both the checksum as well as createCmdMsg()

          /*                         Rudimentary draft of checksum implementation

          char packetArray[packet.length() + 1]; // + 1 for null terminator
          packet.toCharArray(packetArray, packet.length() + 1);
          
          // Check to detect data corruption
          uint8_t check = 0x0;

          if (debug) { Serial.println("\nChecking for data corruption..."); Serial.print("Check is "); Serial.println(check);}
          // XOR all bytes in the recieved message (including the checksum)
          for (uint8_t data : packetArray) {
            if (debug) {Serial.print("data is "); Serial.println(data);}
            check^=data;
            if (debug) {Serial.print("Check is now "); Serial.print(check);Serial.println("\n");}
          }
          if (debug) {
            Serial.print("Final value of check is "); Serial.println(check);
            Serial.print("Check should now equal "); Serial.println(MAGIC_BYTE);
          }

          // Check for corruption
          if (check == MAGIC_BYTE) {
            if (debug) {Serial.println("No data corruption detected");}


          }
          else {
            if (debug) {Serial.println("Data corruption detected");}
          }
                                End of rudimentary draft of checksum implementation
          */

          createCmdMsg(&packet);
          if (msgObj.cmd == 'E') {  // Process as effect message
            processEMessage(&msgObj);

            // Send new signals to each motor
            changeEffect(&drv0, val0, 0);
            changeEffect(&drv1, val1, 1);
            changeEffect(&drv2, val2, 2);
            changeEffect(&drv3, val3, 3);
            changeEffect(&drv4, val4, 4);
            changeEffect(&drv5, val5, 5);
            changeEffect(&drv6, val6, 6);
            if (theDastardlyEighthDriver) {
              changeEffect(&drv7, val7, 7); // THIS LINE IS WHAT TRIGGERS WIFI DISCONNECT
            }
          }
          else if (msgObj.cmd == 'A') { // Process as acceleration message
            if (msgObj.data0 == 0) { // Stop polling accelerometer
              accelToggle = false;
              if (debug) {Serial.println("\nAccelerometer stopped");}
            }
            else {
              accelToggle = true;
            }
          }
        }
        if (accelToggle) {
          getAcceleration();

          // Send acceleration data to client
          client.println(outMsg); // Does this placement give the computer on the other end enough time to read the accel data before client.flush() is called below?
        }
        allDrvPlay(); // Continuously play effects while client connected
        client.flush();
      }
      if (debug) { Serial.println("Client disconnected\n"); }

      // Stop client, accelerometer, and drivers on client disconnect
      client.stop();
      accelToggle = false;
      if (debug) {Serial.println("Accelerometer stopped\n");}
      allDrvStop();

      // TODO: Make LED blink when connected to WiFi but not client. Currently is just on for both cases
    }
  }
  else {
    // LED off if connection lost
    if (debug) { Serial.println("Network connection lost"); }
    digitalWrite(LED_BUILTIN, LOW);

    // Restart WiFi connection
    WiFi.end();
    WiFiConnect();
  }

  //********************************************* Control Via Serial *********************************************

  serialDrvCtrl();
  while (accelToggle) { // Continuously spit out accel data until another message is read over Serial
    getAcceleration();

    // TODO: Save accel data or maybe write it to a file to connected computer via Serial?

    serialDrvCtrl();
    allDrvPlay(); // Continue driver playback if they aren't stopped
  }
  Serial.flush(); // Is this needed? "Waits for the transmission of outgoing serial data to complete"

  // Continuously play effects after message receival
  allDrvPlay();
}
