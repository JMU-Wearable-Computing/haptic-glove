/*
  Will Bradford and Ryan Frost
  Haptic Glove V2 Firmware Utils
*/

#include "utils.h"

/*
  Motor Driver object for tracking motor state

  @param adaDrv: Adafruit driver object
  @param initialized: True if motor is responsive to I2C detection
  @param effect: current effect of motor
*/
struct MotorDriver
{
    Adafruit_DRV2605 *adaDrv;
    bool initialized = false;
    int effect = 0;
    int8_t drvNum;

    MotorDriver(int8_t drvNum)
    {
        this->drvNum = drvNum;
        init();
    }

    void init()
    {
        adaDrv = new Adafruit_DRV2605();

        if (debug)
        {
            Serial.print("Initializing Driver ");
            Serial.println(drvNum);
        }

        // Set multiplexer to a line
        muxSelect(drvNum);

        // Start adafruit motor
        if (!adaDrv->begin())
        {
            if (debug)
            {
                Serial.print("Could not find DRV2605 number ");
                Serial.println(drvNum);
            }
        }

        adaDrv->selectLibrary(1); // Libraries 1-5 are for ERM motors, library 6 is for LRA motors
        adaDrv->setMode(DRV2605_MODE_INTTRIG);

        initialized = true;

        if (debug)
        {
            Serial.print("Driver ");
            Serial.print(drvNum);
            Serial.println(" initialized.");
        }
    }

    void changeEffect(int effectNum)
    {
        if (effectNum < 0 || effectNum > 123)
        {
            if (debug)
            {
                Serial.print("Effect ID Number must be between 0 and 123 inclusive, actual value was: ");
                Serial.println(effectNum);
            }

            return;
        }

        muxSelect(drvNum);

        if (effectNum > 0)
        { // Set new playback effect
            if (debug)
            {
                Serial.print("Setting the effect ID of driver ");
                Serial.print(drvNum);
                Serial.print(" to ");
                Serial.println(effectNum);
            }

            adaDrv->setWaveform(0, effectNum); // Desired effect
            adaDrv->setWaveform(1, 0);         // End waveform

            if (debug)
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
            if (debug)
            {
                Serial.print("Stopping driver number ");
                Serial.print(drvNum);
                Serial.println(".");
            }

            adaDrv->stop();

            if (debug)
            {
                Serial.print("Driver number ");
                Serial.print(drvNum);
                Serial.println(" stopped.");
            }
        }
        if (debug)
        {
            Serial.println();
        } // Print newline for easier reading
        this->effect = effectNum;
    }

    void muxSelect(uint8_t i)
    {
        Wire.beginTransmission(MUXADDR);
        Wire.write(1 << i);
        Wire.endTransmission();
    }
};

struct MotorDriverSet
{
    MotorDriver **drivers;
    size_t numDrvs;

    MotorDriverSet(size_t numDrvs)
    {
        if (numDrvs < 0 || numDrvs > 7)
        {
            if (debug)
            {
                Serial.print("Drivier initialization failed: numDrvs must be between 0 and 7 inclusive, actual value was: ");
                Serial.println(numDrvs);
            }
            return;
        }
        drivers = new MotorDriver *[numDrvs];
        for (size_t i = 0; i < numDrvs; i++)
        {
            drivers[i] = new MotorDriver(i);
        }
    }

    void processEMessage(CommandMessage msg)
    {
        if (debug)
        {
            Serial.println("Processing as an effect message.");
        }

        // Assign effect numbers
        for (size_t i = 0; i < numDrvs; i++)
        {
            if (debug)
            {
                Serial.print("Motor ");
                Serial.print(i);
                Serial.print(" Effect = ");
                Serial.println(msgToSend->data[i]);
            }
            drivers[i]->changeEffect(msgToSend->data[i]);
        }

        if (debug)
        {
            Serial.println("\n");
        } // Print 2 newlines for easier reading
    }
};

// General message structure
struct CommandMessage
{
    String packet;
    char cmd;
    int *data;

    CommandMessage(size_t numDrvs)
    {
        data = new int[numDrvs];
    }

    void recievePacket()
    {
        packet = String(Serial.readStringUntil('\n'));
        processPacket();
    }

    void recievePacket(WiFiClient client)
    {
        packet = String(client.readStringUntil('\n'));
        processPacket();
    }

    void processPacket()
    {
        if (debug)
        {
            Serial.print("\nMessage reads ");
            Serial.println(packet);
        }

        // Split message and assign values to Motor Signals
        // Make msg into an array
        int msgLength;

        if (packet.length() < 9)
        { // Allows for user to pass messages that are < the number of parameters needed to create a Message object
            if (debug)
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

            if (debug)
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

        if (debug)
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

        // Test if valid cmd
        if (validateCmd(*msgPieces[0]))
        {

            if (debug)
            {
                Serial.println("Command validated");
                Serial.println("Created a message object with the following parameters:");
            }

            // Create Message object; ignore checksum at the end
            cmd = *msgPieces[0];
            if (debug)
            {
                Serial.print("CommandObject cmd = ");
                Serial.println(cmd);
            }

            for (int i = 0; i < max_motors; i++)
            {
                data[i] = atoi(msgPieces[i + 1]);
                if (debug)
                {
                    Serial.print("CommandObject data ");
                    Serial.print(i);
                    Serial.print(" = ");
                    Serial.println(data[i]);
                }
            }
        }
        else
        { // Handle invalid cmd letters; retry input
            if (debug)
            {
                Serial.println("Invalid Message type received.");
            }
        }
    }

    void runCommand(MotorDriverSet driverSet)
    {
        if (cmd == 'E')
        {
            driverSet.processEMessage(*this);
        }
        else if (cmd == 'A')
        { // Process as acceleration message
            if (data[0] == 0)
            { // Stop polling accelerometer
                accelToggle = false;
                if (debug)
                {
                    Serial.println("\nAccelerometer stopped");
                }
            }
            else
            {
                accelToggle = true;
            }
        }
    }
};



bool IMU_INITIALIZED = false;

// Connect to WiFi
void WiFiConnect()
{
    // Check if static IP address is needed and configure network
    if (STATIC_IP)
    {
        WiFi.config(local_IP, dns, gateway, subnet);
        if (debug)
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
    if (debug)
    {
        Serial.println("Connecting to WiFi...");
    }
    while (WiFi.status() != WL_CONNECTED)
    {
        if (debug)
        {
            Serial.print(".");
        }
        delay(500);
    }

    // TODO: blink LED when connected to WiFi

    // Open TCP server
    server.begin();
    if (debug)
    { // Print network details
        Serial.print("\nConnected to ");
        Serial.println(ssid);
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        Serial.print("on port ");
        Serial.println(port);
    }
    // TODO: LED blinking if connected to WiFi but not client. Currently is just on
    digitalWrite(LED_BUILTIN, HIGH);
}

// Select which driver to talk to

// Initialize all available drivers

// Test if passed cmd is valid
bool validateCmd(char cmd)
{
    for (char letter : msgTypes)
    {
        if (letter == cmd)
        {
            return true;
        }
    }
    return false;
}

// Change the playback effect pattern of the DRV2605 drivers

// Parse received packet

// Process Message object as an eMessage

// Process Message object as an aMessage
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
        if (debug)
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
        if (debug)
        {
            Serial.println("ERROR: Failed to read acceleration");
        }
    }
}

// Stop all motor drivers
void allDrvStop(MotorDriver *drvs[])
{
    for (int i = 0; i < max_motors; i++)
    {
        drvs[i]->effect = 0;
        changeEffect(drvs[i], 0, 0);
    }
}

// Play current effect on all drivers
void allDrvPlay(MotorDriver *drvs[])
{
    for (int i = 0; i < max_motors; i++)
    {
        if (drvs[i]->effect != 0)
        {
            muxSelect(i);
            drvs[i]->adaDrv->go();
        }
    }
}