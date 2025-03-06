#ifndef UTILS_H
#define UTILS_H

#include <Wire.h>
#include <Adafruit_DRV2605.h>
#include <WiFi.h>
#include <Arduino.h>
#include <math.h>
#include <SPI.h>
#include <Arduino_LSM6DS3.h>

// Constants and definitions
#define DEVICE_ID 10        // Set device ID used in static IP (Acceptable ranges are 10-100)
#define STATIC_IP true      // Toggle static or dynamic IP
#define DEBUG true          // Toggle debug mode (Toggle program being verbose)
#define WIFI_PORT 8888           // Port number for WiFi server
#define MAX_MOTORS 8        // Maximum motors supported 0 to 8 inclusive

#define MUXRST 17           // Mux Reset pin is tied to Arduino pin D17 for on-demand resets
#define MUXADDR 0x70        // Mux I2C address
#define ssid "WearablesLab" // Network SSID
#define password ""         // Network password

// Pin out for board:
// https://docs.espressif.com/projects/esp-idf/en/v5.1/esp32s2/hw-reference/esp32s2/user-guide-saola-1-v1.2.html
// SDA: GPIO8 on board
// SCL: GPIO9 on board
#define SDA_PIN 8
#define SCL_PIN 9

// Forward declarations
struct MotorDriver;
struct MotorDriverSet;
struct CommandMessage;
struct WiFiObj;
struct IMUObj;

// Global variables
extern MotorDriverSet* drvs;
extern CommandMessage* command;
extern WiFiObj* wifiObj;
extern IMUObj* imuObj;

// MotorDriver struct for controlling motors
struct MotorDriver {
    Adafruit_DRV2605 *adaDrv;
    bool initialized;
    int effect;
    int8_t drvNum;

    MotorDriver(int8_t drvNum);
    void init();
    void changeEffect(int effectNum);
    void go();
    void muxSelect(uint8_t i);
};

// MotorDriverSet struct for managing multiple MotorDriver objects
struct MotorDriverSet {
    MotorDriver **drivers;
    size_t numDrvs;

    MotorDriverSet(size_t numDrvs);
    void processEMessage(CommandMessage msg);
    void go();
    void stop();
    void cycle();
};

// CommandMessage struct for parsing messages
struct CommandMessage {
    MotorDriverSet* drivers;
    String packet;
    char cmd;
    int* data;

    CommandMessage(size_t numDrvs, MotorDriverSet* drivers);
    void recievePacket();
    void recievePacket(WiFiClient client);
    void processPacket();
    void runCommand();
};

struct WiFiObj {
    WiFiServer* server;
    IPAddress* local_IP;
    IPAddress* gateway;
    IPAddress* dns;
    IPAddress* subnet;
    WiFiClient* client;

    WiFiObj(WiFiServer& server, IPAddress local_IP, IPAddress gateway, IPAddress dns, IPAddress subnet);
    void connect();
};

struct IMUObj {
    float accelX;
    float accelY;
    float accelZ;
    float mag;
    bool accelToggle;
    bool IMU_INITIALIZED;
    String outMsg;

    IMUObj();
    void initialize();
    void getAcceleration();
};

#endif
