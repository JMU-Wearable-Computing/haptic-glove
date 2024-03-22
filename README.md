# haptic-glove

## PCB (Printed Circuit Board)

### Schematic V2.1
<img src = "Images/Board Photos/V2.1/glove-2.1-sch.png" />

### Layout V2.1
<img src = "Images/Board Photos/V2.1/glove-V2.1-top.png" />
<img src = "Images/Board Photos/V2.1/glove-V2.1-bottom.png" />

#### PCB Edit History
##### V2.0
- Initial board redesign
##### V2.1
- Changed part J1 to be an accurate JST-PH connector
- Shifted Arduino placement down 1 mm to allow for more clearance between the Arduino and the motor header pins
- Added graphic to denote onboard IMU directions
- Added a spot on the back of the board to write the board's device ID
- Shifted some silkscreen placements so that part names are not cut off by pads
  
## Eagle PCB Set-Up

### OSHPark Plugin
The OSHPark Eagle plugin includes OSHPark design rules and allows the user to send the .brd file directly to an OSHPark cart. See the [OSHPark-Eagle-Tools GitHub](https://github.com/OSHPark/OSHPark-Eagle-Tools)

### Libraries
Included in the repository are:
1. TCA9548APWR.lbr (I2C multiplexer)
2. 1769.lbr (JST-PH connector)
3. SparkFun-Eagle-Libraries-main.zip

## Arduino Nano Arduino IDE setup 

### Correct IDE version
Arduino IDE 2.X.X

### Correct board library and name:
#### Board Library
Arduino SAMD Boards (32-bits ARM Cortex-M0+)

#### Board Name
Arduino NANO 33 IoT

### Arduino Libraries
 
1. Adafruit_DRV2605.h
2. Arduino_LSM6DS3.h
3. WiFiNINA.h

## Communicating with Nano 33 IoT

Nano 33 IoT can be communicated with via TCP socket connection.
Network credentials can be modified with the "ssid" and "password" variables within the Arduino code.
When booted, the Nano 33 IoT establishes a user definable static IP.

### Onboard LED state meanings (TODO)
|State|Meaning|
--- | --- |
|OFF|Not connected to network|
|BLINKING|Connected to user specified network (not currently implemented)|
|SOLID|TCP client connected and ready for messages|

### Message format
Messages follows the format: <kbd>X,n01,n02,n03,n04,n05,n06,n07,n08</kbd>

X is a char that signifies the message type. nXX is a number.
Negative numbers will be ignored and the playback of the current haptic effect will continue.
0 will stop the corresponding driver.
All decimals will be rounded DOWN.
Each segment of the message correspondes to the strength of a specific haptic driver, where n01 controls driver 1, n02 controls driver 2, and so on.

#### Effect Messages
For messages of type 'E', numbers [1, 123] will set the playback effect of the corresponding driver.
Numbers higher than 123 will set the playback effect to effect # 123.

##### Example
The message <kbd>'E',100,43,55,1,123,34,99,2</kbd> will cause motor one to activate using haptic effect # 100, motor two to activate using haptic effect # 43, and so on. Passing the message <kbd>'E',0,-1,100.7,9999,0,0,0,0</kbd> afterwards will stop motors 1, 5, 6, 7, and 8. Motor 2 will remain activated with the same haptic effect as before (# 43), motor 3 will activate using haptic effect # 100, and motor 4 will activate using haptic effect # 123.

#### Acceleration Messages
For messages of type 'A', numbers are not required. They may be included, but will not be used by the Arduino. This message returns the acceleration data at that instant and sends it to the client.

##### Example
TODO

## Tutorials
### Arduino IDE setup
This will teach you how to set up the Arduino IDE for use of the haptic glove. Prior to following this tutorial, you should already have the Arduino IDE downloaded.

1. Open <kbd>firmware-2.0.ino</kbd>. <kbd>network_cred.h</kbd> should automatically open in a separate tab
2. Click the <kbd>network_cred.h</kbd> tab at the top and input your WiFi credentials. Press <kbd>Command</kbd> + <kbd>S</kbd> to save your edits on a Mac (<kbd>Control</kbd> + <kbd>S</kbd> on Windows).
3. Open the Boards Manager by clicking the correct icon on the left of the IDE. Search for "nano 33 iot". The one board library that should be shown is <kbd>Arduino SAMD Boards (32-bits ARM Cortex-M0+)</kbd>. Install this library. Feel free to install a newer version than what is shown in the picture.

<img src = "Images/Tutorial Photos/Arduino IDE set up/Board manager screenshot.png" />

4. Open the Library manager by clicking the correct icon on the left of the IDE. Search for and install <kbd>Adafruit DRV2605 Library</kbd>, <kbd>Arduino_LSM6DS3</kbd> and <kbd>WiFiNINA</kbd>. Feel free to install newer versions than what are shown in the pictures.

<img src = "Images/Tutorial Photos/Arduino IDE set up/DRV2605 library screenshot.png" />
<img src = "Images/Tutorial Photos/Arduino IDE set up/LSM6dS3 library screenshot.png" />
<img src = "Images/Tutorial Photos/Arduino IDE set up/WiFiNINA library screenshot.png" />

5. Navigate to <kbd>Tools</kbd>><kbd>Board</kbd>><kbd>Arduino</kbd>><kbd>SAMD Boards (32-bits ARM Cortex-M0+)</kbd> and select <kbd>Arduino Nano 33 IoT</kbd> as the board.
6. Congratulations! Arduino IDE is now set up to be used with the haptic glove.

### Communicating with the Arduino via serial port
This will teach you how to send messages to the Arduino via the serial port that will control the haptic motors and the onboard IMU.

#### Initial Arduino set up
1. Complete the "Arduino IDE set up" tutorial.
2. Set the user-definable variables in the firmware. The variable `DEVICE_ID` does not matter when using serial communication.

<img src = "Images/Tutorial Photos/Initial Arduino set up/User Definable screenshot.png" />

3. Connect the Arduino to your computer via USB, ensure the correct board and port are selected in the Arduino IDE, and upload the firmware by clicking the arrow button in the top left of the IDE.

#### Example Use
TODO

### Communicating with the Arduino via TCP socket connection
This will teach you how to send messages to the Arduino via a TCP socket to control the haptic motors and the onboard IMU.

#### Initial Arduino set up
1. Complete the "Arduino IDE set up" tutorial.
2. Set the user-definable variables in the firmware. Be sure to set `DEVICE_ID` to a unique integer [10, 100].

<img src = "Images/Tutorial Photos/Initial Arduino set up/User Definable screenshot.png" />

3. Connect the Arduino to your computer via USB, ensure the correct board and port are selected in the Arduino IDE, and upload the firmware by clicking the arrow button in the top left of the IDE.
4. Once uploaded, you can safely unplug the Arduino from your computer. Congratulations! Your Arduino now has the necessary software and is ready for use with the haptic glove.

#### Setting up Python
TODO

#### Example Use
TODO

