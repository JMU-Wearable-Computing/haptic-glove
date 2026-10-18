/*
  Will Bradford, Ryan Frost and Tony Postak
  Haptic Glove V2 Firmware

  Due to C++ magic, message parser behavior is weird when passing values for less than 8 motors. Pass values for
    all 8 to be safe

  This version of the firmware is able to build two different binaries, one for the ESP32 and another for the Nano33
  When building, platformIO should compile two different builds using the compiler directives seen throughout the codebase.
  When uploading to a board, platformIO will attempt to upload both firmwares, and will likely discover one of them is not compatable.

  test messege: E,100,43,55,1,123,34,99,2
*/

#include "utils.h"


MotorDriverSet* drvs;
CommandMessage* command;
WiFiObj* wifiObj;
IMUObj* imuObj;
bool wifiDisconnected = false;
#if defined(CONFIG_IDF_TARGET_ESP32S2)
  WiFiServer* server = new WiFiServer(WIFI_PORT);
#endif

void setup()
{
  Serial.begin(9600);  
  pinMode(LED_BUILTIN, OUTPUT);
  delay(2000);
  
  #if defined(ARDUINO_ARCH_SAMD)
  Wire.begin();
	#endif
  #if defined(CONFIG_IDF_TARGET_ESP32S2)
  Wire.begin(SDA_PIN, SCL_PIN);
  pinMode(CLIENT_CONNECTED_PIN, OUTPUT);
  pinMode(MESSAGE_RECEIVED_PIN, OUTPUT);
	#endif

  // Start serial connection
  if (DEBUG) {
    while (!Serial) // This will cause an issue if you don't open the serial port on computer
    {
      delay(1);
    }
    Serial.println("Booting Up");
  }

  // Connect to the multiplexer if the board is ESP32
  #if defined(CONFIG_IDF_TARGET_ESP32S2)
    Wire.beginTransmission(MUXADDR);
    byte error = Wire.endTransmission();

    if (error != 0) {
      while (true) {
        // Flash LED
        Serial.println("Multiplexer not found");
        delay(500);
      }
    }
	#endif

  // Tie mux RST high
  pinMode(MUXRST, OUTPUT);
  digitalWrite(MUXRST, HIGH);

  // Initialize global variables
  drvs = new MotorDriverSet(MAX_MOTORS);
  command = new CommandMessage(MAX_MOTORS, drvs);
  wifiObj = new WiFiObj(
    #if defined(CONFIG_IDF_TARGET_ESP32S2)
      *server,                          // ESP server
	  #endif
    #if defined(ARDUINO_ARCH_SAMD)
      WiFiServer(WIFI_PORT),              // Nano server
	  #endif
    IPAddress(172, 16, 1, DEVICE_ID),   // local_IP
    IPAddress(172, 16, 1, 1),           // gateway
    IPAddress(172, 16, 1, 1),           // dns
    IPAddress(255, 255, 0, 0)           // subnet
  );
  imuObj = new IMUObj();

  Serial.print("Num drivers: ");
  Serial.println(drvs->numDrvs);

  // Sequentially activate/deactivate drivers
  if (DEBUG)
  {
    Serial.println("Cycling drivers\n");
  }

  drvs->cycle();

  if (DEBUG)
  {
    Serial.println("Drivers cycled\n");
  }

  // Connect to WiFi
  wifiObj->connect();

  // Initialize accelerometer
  imuObj->initialize();

  if (DEBUG)
  {
    Serial.println("System ready for use!");
  }
}

void loop()
{

  //********************************************** Control Via WiFi **********************************************

  // Execute if WiFi connected
  if (WiFi.status() == WL_CONNECTED)
  {
    // Check if a client has connected
    WiFiClient client = wifiObj->server->available();

    // TODO: LED blinking if connected to WiFi but not client. Currently is just on
    if (client)
    { // This evaluates as 0 unless a message has appeared over the TCP socket
      if (client.connected())
      {
        // TODO: LED on if client connected. Currently is on if connected to WiFi
        if (DEBUG)
        {
          Serial.println("Client connected");
        }
      }
      // While client is connected, keep reading messages from client
      while (client.connected())
      {
        #if defined(CONFIG_IDF_TARGET_ESP32S2)
          digitalWrite(CLIENT_CONNECTED_PIN, HIGH);
	      #endif
        // If a message exists, read it
        if (client.available() > 0)
        {
          // TODO: turn packet into a char array from inception to simplify later code in both the checksum as well as createCmdMsg()

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
          #if defined(CONFIG_IDF_TARGET_ESP32S2)
            digitalWrite(MESSAGE_RECEIVED_PIN, HIGH);
	        #endif
          command->recievePacket(client);
          #if defined(CONFIG_IDF_TARGET_ESP32S2)
            digitalWrite(MESSAGE_RECEIVED_PIN, LOW);
	        #endif
        }
        #if defined(ARDUINO_ARCH_SAMD)
          if (imuObj->accelToggle)
          {
            imuObj->getAcceleration();
            
            // Send acceleration data to client
            client.println(imuObj->outMsg); // Does this placement give the computer on the other end enough time to read the accel data before client.flush() is called below?
          }
        #endif
        drvs->go();
        #if defined(ARDUINO_ARCH_SAMD)
          ; // Continuously play effects while client connected
          client.flush();
	      #endif
      }
      #if defined(CONFIG_IDF_TARGET_ESP32S2)
        digitalWrite(CLIENT_CONNECTED_PIN, LOW);
	    #endif
      if (DEBUG)
      {
        Serial.println("Client disconnected\n");
      }

      // Stop client, accelerometer, and drivers on client disconnect
      client.stop();
      imuObj->accelToggle = false;
      if (DEBUG)
      {
        Serial.println("Accelerometer stopped\n");
      }
      drvs->stop();

      // TODO: Make LED blink when connected to WiFi but not client. Currently is just on for both cases
    }
  }
  else if (wifiDisconnected == false) // This only needs to run once after the Wifi connection is gone or isn't initiated
  {
    // LED off if connection lost
    if (DEBUG)
    {
      Serial.println("Network connection lost");
    }
    digitalWrite(LED_BUILTIN, LOW);

    // Restart WiFi connection
    #if defined(ARDUINO_ARCH_SAMD)
      WiFi.end();
	  #endif
    #if defined(CONFIG_IDF_TARGET_ESP32S2)
      WiFi.disconnect();
      WiFi.mode(WIFI_OFF);
	  #endif
    wifiObj->connect();

    wifiDisconnected = true;
  }

  //********************************************* Control Via Serial *********************************************
  if (Serial.available() > 0)
  {
    command->recievePacket();
  }
  #if defined(ARDUINO_ARCH_SAMD)
    while (imuObj->accelToggle)
    { // Continuously spit out accel data until another message is read over Serial
      imuObj->getAcceleration();

      // TODO: Save accel data or maybe write it to a file to connected computer via Serial?
      if (Serial.available() > 0)
      {
        command->recievePacket();
      }
      drvs->go();
    }
    Serial.flush(); // Is this needed? "Waits for the transmission of outgoing serial data to complete"
	#endif

  // Continuously play effects after message receival
  drvs->go();
}
