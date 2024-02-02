# haptic-glove

## Wiring diagram
TODO

## Circuit board

TODO

## Arduino Nano Arduino IDE setup 

### Guide:
TODO

### Board manager URL:
TODO

### Correct board type:
Arduino NANO 33 IoT

### Arduino Libraries
 
1. Adafruit_DRV2605.h
2. Arduino_LSM6DS3.h
3. WiFiNINA.h

## Communicating with Nano 33 IoT

Nano 33 IoT can be communicated with via TCP socket connection.
Network credentials can be modified with the "ssid" and "password" variables within the Arduino code.
When booted, the Nano 33 IoT establishes a user definable static IP.

### Message format
Messages follows the format: /n01/n02/n03/n04  
nXX is a number of length 3 between 0 and 255.
Each segment of the message correspondes to the strength of a specific motor.
Where n01 controls motor 1, n02 controls motor 2 and so on.
