/*
  Will Bradford and Ryan Frost
  Haptic Glove V2 Firmware Utils
*/

#include "utils.h"


// Global variables
MotorDriverSet* drvs;
CommandMessage* command;

float accelX = 0;
float accelY = 0;
float accelZ = 0;
float mag = 0;
bool accelToggle = false;
bool IMU_INITIALIZED = false;
String outMsg;

// Wifi settings
WiFiServer server(WIFI_PORT);
IPAddress local_IP(172, 16, 1, DEVICE_ID);

IPAddress gateway(172, 16, 1, 1);
IPAddress dns(172, 16, 1, 1);
IPAddress subnet(255, 255, 0, 0);

/*
  Motor Driver object for tracking motor state

  @param adaDrv: Adafruit driver object
  @param initialized: True if motor is responsive to I2C detection
  @param effect: current effect of motor
*/
MotorDriver::MotorDriver(int8_t drvNum)
{
    this->drvNum = drvNum;
    init();
}

void MotorDriver::init()
{
    adaDrv = new Adafruit_DRV2605();

    if (DEBUG)
    {
        Serial.print("Initializing Driver ");
        Serial.println(drvNum);
    }

    // Set multiplexer to a line
    muxSelect(drvNum);

    // Start adafruit motor
    if (!adaDrv->begin())
    {
        if (DEBUG)
        {
            Serial.print("Could not find DRV2605 number ");
            Serial.println(drvNum);
        }
    }

    adaDrv->selectLibrary(1); // Libraries 1-5 are for ERM motors, library 6 is for LRA motors
    adaDrv->setMode(DRV2605_MODE_INTTRIG);

    initialized = true;

    if (DEBUG)
    {
        Serial.print("Driver ");
        Serial.print(drvNum);
        if (initialized) 
        {
            Serial.println(" initialized.");
        }
        else
        {
            Serial.println(" not initialized.");
        }
    }
}

void MotorDriver::changeEffect(int effectNum)
{
    muxSelect(drvNum);

    if (effectNum > 0 && effectNum <= 123)
    { // Set new playback effect
        if (DEBUG)
        {
            Serial.print("Setting the effect ID of driver ");
            Serial.print(drvNum);
            Serial.print(" to ");
            Serial.println(effectNum);
        }

        adaDrv->setWaveform(0, effectNum); // Desired effect
        adaDrv->setWaveform(1, 0);         // End waveform

        if (DEBUG)
        {
            Serial.print("Effect ID of driver ");
            Serial.print(drvNum);
            Serial.print(" set to ");
            Serial.println(effectNum);
        }

        adaDrv->go();
    }
    else if (effectNum == 0)
    { // Stop driver
        if (DEBUG)
        {
            Serial.print("Stopping driver number ");
            Serial.print(drvNum);
            Serial.println(".");
        }

        adaDrv->stop();

        if (DEBUG)
        {
            Serial.print("Driver number ");
            Serial.print(drvNum);
            Serial.println(" stopped.");
        }
    }
    else
    {
        if (DEBUG)
        {
            Serial.print("Effect ID Number must be between 0 and 123 inclusive, actual value was: ");
            Serial.println(effectNum);
        }

        return;
    }
    if (DEBUG)
    {
        Serial.println();
    } // Print newline for easier reading
    this->effect = effectNum;
}

void MotorDriver::go()
{
    if (effect != 0)
    {
        muxSelect(drvNum);
        adaDrv->go();
    }
}

void MotorDriver::muxSelect(uint8_t i)
{
    Wire.beginTransmission(MUXADDR);
    Wire.write(1 << i);
    Wire.endTransmission();
}

MotorDriverSet::MotorDriverSet(size_t numDrvs)
{
    if (numDrvs >= 0 && numDrvs <= 8)
    {
        this->numDrvs = numDrvs;
        drivers = new MotorDriver *[numDrvs];
        for (int i = 0; i < (int)numDrvs; i++)
        {
            drivers[i] = new MotorDriver(i);
        }
    }
    else
    {
        if (DEBUG)
        {
            Serial.print("Drivier initialization failed: numDrvs must be between 0 and 7 inclusive, actual value was: ");
            Serial.println(numDrvs);
        }
        return;
    }
}

void MotorDriverSet::processEMessage(CommandMessage msg)
{
    if (DEBUG)
    {
        Serial.println("Processing as an effect message.");
    }

    // Assign effect numbers
    for (int i = 0; i < (int)numDrvs; i++)
    {
        if (DEBUG)
        {
            Serial.print("Motor ");
            Serial.print(i);
            Serial.print(" Effect = ");
            Serial.println(msg.data[i]);
        }
        drivers[i]->changeEffect(msg.data[i]);
    }

    if (DEBUG)
    {
        Serial.println("\n");
    } // Print 2 newlines for easier reading
}

void MotorDriverSet::go()
{
    for (int i = 0; i < (int)numDrvs; i++)
    {
        drivers[i]->go();
    }
}

void MotorDriverSet::stop()
{
    for (int i = 0; i < (int)numDrvs; i++)
    {
        drivers[i]->changeEffect(0);
    }
}

void MotorDriverSet::cycle()
{
    for (int i = 0; i < (int)numDrvs; i++) 
    {
        drivers[i]->changeEffect(64);
        drivers[i]->adaDrv->go();
        delay(500);
    }

    stop();
}

CommandMessage::CommandMessage(size_t numDrvs, MotorDriverSet drivers)
{
    data = new int[numDrvs];
    this->drivers = &drivers;
}

void CommandMessage::recievePacket()
{
    packet = String(Serial.readStringUntil('\n'));
    processPacket();
}

void CommandMessage::recievePacket(WiFiClient client)
{
    packet = String(client.readStringUntil('\n'));
    processPacket();
}

void CommandMessage::processPacket()
{
    if (DEBUG)
    {
        Serial.print("\nMessage reads ");
        Serial.println(packet);
    }

    // Split message and assign values to Motor Signals
    // Make msg into an array
    int msgLength;

    if (packet.length() < 9)
    { // Allows for user to pass messages that are < the number of parameters needed to create a Message object
        if (DEBUG)
        {
            Serial.print("Message length is ");
            Serial.print(packet.length());
            Serial.println(", but it was forced to be 9.");
        }
        msgLength = 9;
    }
    else
    {
        msgLength = packet.length() + 1; // Add 1 character for null terminator

        if (DEBUG)
        {
            Serial.print("Message length is ");
            Serial.println(msgLength);
        }
    }

    char msgArray[msgLength];                // Create array
    packet.toCharArray(msgArray, msgLength); // Copy msg to previously created array

    /*
        **************************************************************************************************************
        strtok() has state and remembers the delimeter. Be carefel thar be dragons!!!!!!!!
        **************************************************************************************************************
    */

    char *msgPieces[msgLength]; // An array of pointers to the pieces of msg after strtok()
    char *ptr = NULL;

    byte index = 0;
    ptr = strtok(msgArray, ","); // Delimiter
    while (ptr != NULL)
    { // Parse the message and place pieces into array
        msgPieces[index] = ptr;
        index++;
        ptr = strtok(NULL, ",");
    }

    if (DEBUG)
    {
        Serial.println("The message pieces detected are:");
        for (int n = 0; n < index; n++)
        {
            Serial.print(n);
            Serial.print("  ");
            Serial.println(msgPieces[n]);
        }
        Serial.println(); // Print newline for easier reading
    }

    // Create Message object; ignore checksum at the end
    cmd = *msgPieces[0];
    if (DEBUG)
    {
        Serial.print("CommandObject cmd = ");
        Serial.println(cmd);
    }

    for (int i = 0; i < (int)drivers->numDrvs; i++)
    {
        data[i] = atoi(msgPieces[i + 1]);
        if (DEBUG)
        {
            Serial.print("CommandObject data ");
            Serial.print(i);
            Serial.print(" = ");
            Serial.println(data[i]);
        }
    }

    runCommand();
}

void CommandMessage::runCommand()
{
    if (cmd == 'E')
    {
        drivers->processEMessage(*this);
    }
    else if (cmd == 'A')
    { // Process as acceleration message
        if (data[0] == 0)
        { // Stop polling accelerometer
            accelToggle = false;
            if (DEBUG)
            {
                Serial.println("\nAccelerometer stopped");
            }
        }
        else if (data[0] == 1)
        {
            accelToggle = true;
        }
    }
    else
    {
        if (DEBUG)
        {
            Serial.print("Command not supported: ");
            Serial.println(cmd);
        }
    }
}

// Connect to WiFi
void WiFiConnect()
{
    // Check if static IP address is needed and configure network
    if (STATIC_IP)
    {
        WiFi.config(local_IP, dns, gateway, subnet);
        if (DEBUG)
        {
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
    }

    // Configure WiFi connection, start to connect
    WiFi.begin(ssid, password); // Connect to WiFi
    delay(100);                 // Is this needed?

    // Wait for connection
    if (DEBUG)
    {
        Serial.println("Connecting to WiFi...");
    }
    while (WiFi.status() != WL_CONNECTED)
    {
        if (DEBUG)
        {
            Serial.print(".");
        }
        delay(500);
    }

    // TODO: blink LED when connected to WiFi

    // Open TCP server
    server.begin();
    if (DEBUG)
    { // Print network details
        Serial.print("\nConnected to ");
        Serial.println(ssid);
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        Serial.print("on port ");
        Serial.println(WIFI_PORT);
    }
    // TODO: LED blinking if connected to WiFi but not client. Currently is just on
    digitalWrite(LED_BUILTIN, HIGH);
}

void getAcceleration()
{
    if (IMU.accelerationAvailable())
    { // If there is new acceleration data available

        // Measure acceleration data
        IMU.readAcceleration(accelX, accelY, accelZ);

        // Calculate magnitude
        mag = sqrt(pow(accelX, 2) + pow(accelY, 2) + pow(accelZ, 2));

        // Update message to send
        outMsg = String(accelX) + "," + String(accelY) + "," + String(accelZ) + "," + String(mag);
        if (DEBUG)
        {
            Serial.println("\nAcceleration in G's");
            Serial.println("X\tY\tZ\tMag");
            Serial.print(accelX);
            Serial.print('\t');
            Serial.print(accelY);
            Serial.print('\t');
            Serial.print(accelZ);
            Serial.print('\t');
            Serial.println(mag);

            Serial.print("outMsg = ");
            Serial.println(outMsg);
        }
        // Wait for new acceleration data to populate
        // TODO: Is it beneficial to have a dedicated global variable that stores the accelerometer's sample rate?
        delay((1 / IMU.accelerationSampleRate()) * 1000); // Comment out if sample rate is low so that this doesn't delay new messages from being read
    }
    else
    {
        if (DEBUG)
        {
            Serial.println("ERROR: Failed to read acceleration");
        }
    }
}