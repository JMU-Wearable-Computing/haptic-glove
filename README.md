# haptic-glove

## Haptic Effect Waveforms
<img src = "Images/DRV2605 Waveforms.png" />

[Image source](https://learn.adafruit.com/assets/72593)

## PCB (Printed Circuit Board)

### Schematic V2.1
<img src = "Images/Board Photos/V2.1/glove-2.1-sch.png" />

### Layout V2.1
<img src = "Images/Board Photos/V2.1/glove-V2.1-top.png" />
<img src = "Images/Board Photos/V2.1/glove-2.1-bottom.png" />

#### PCB Edit History
##### V2.0
- Initial board redesign
##### V2.1
- Shifted Arduino placement down 1 mm to allow for more clearance between the Arduino and the motor header pins
- Added graphic to denote onboard IMU directions
- Added a spot on the back of the board to write the board's device ID
- Shifted some silkscreen placements so that part names are not cut off by pads
- Added text to denote correct Arduino orientation
  
## Eagle PCB Set-Up

### OSHPark Plugin
The OSHPark Eagle plugin includes OSHPark design rules and allows the user to send the .brd file directly to an OSHPark cart. See the [OSHPark-Eagle-Tools GitHub](https://github.com/OSHPark/OSHPark-Eagle-Tools)

### Libraries
Included in the repository are:
1. TCA9548APWR.lbr (I2C multiplexer)
2. SparkFun-Eagle-Libraries-main.zip

## VSCode PlatformIO IDE Setup

### Board Version
esp32-s2-saola-1

### Libraries
Adafruit BusIO
Adafruit DRV2605 Library
Arduino_LSM6DS3

## Communicating with ESP32

ESP32 can be communicated with via TCP socket connection.
Network credentials can be modified with the `ssid` and `password` variables in utils.h.
When booted, the ESP32 establishes a user definable static IP.

### Onboard LED state meanings
|State|Meaning|
--- | --- |
|OFF|Not connected to network|
|ON|Connected to user specified network|

### Message format
Messages follows the format: `X,n01,n02,n03,n04,n05,n06,n07,n08`

X is a char that signifies the message type. nXX is a number.
Negative numbers will be ignored and the playback of the current haptic effect will continue.
0 will stop the corresponding driver.
All decimals will be rounded DOWN.
Each segment of the message correspondes to the strength of a specific haptic driver, where n01 controls driver 1, n02 controls driver 2, and so on.

#### Effect Messages
For messages of type 'E', numbers [1, 123] will set the playback effect of the corresponding driver.
Numbers higher than 123 will set the playback effect to effect # 123.

##### All Stop Message
Should you want to halt the haptic playback of all drivers, simply passing `'E'` as the entire effect message will do this.

##### Example
The message `'E',100,43,55,1,123,34,99,2` will cause driver one to activate using haptic effect # 100, driver two to activate using haptic effect # 43, and so on. Passing the message `'E',0,-1,100.7,9999,0,0,0,0` afterwards will stop drivers 1, 5, 6, 7, and 8. Driver 2 will remain activated with the same haptic effect as before (# 43), driver 3 will activate using haptic effect # 100, and driver 4 will activate using haptic effect # 123.

#### Acceleration Messages (Deprecated on ESP32, no Accelerometer)
For messages of type 'A', numbers are used to toggle the continuous collection of acceleration data. Only one number should be passed. Passing the number zero will halt data collection, while any other number will resume data collection. For simplicity's sake, it is recommended to only use the number one to resume data collection. Once started, data will be continuously returned and sent to the client until another acceleration message is recieved that instructs the system to halt data collection.

##### Example
The message `'A',1` will begin continuous acceleration data collection and sending. The message `'A',0` will halt all acceleration data collection and sending.

## Tutorials
### PlatformIO Setup
This will teach you how to set up PlatformIO for use of the haptic glove. Prior to following this tutorial, you should already have VSCode downloaded.

1. Add the PlatformIO extension to VSCode
<img src = "Images/Tutorial Photos/PlatformIO Setup/install_extension.png" />

2. Navigate to PlatformIO Home (Ctrl + Shift + P to search for program)
<img src = "Images/Tutorial Photos/PlatformIO Setup/navigate_to_home.png" />

3. Select "New Project"
<img src = "Images/Tutorial Photos/PlatformIO Setup/add_new_project.png" />

4. Search for ESP32-S2-Saola-1 Board
<img src = "Images/Tutorial Photos/PlatformIO Setup/new_project_board_selection.png" />

5. Create Project

6. Navigate to PlatformIO Home again

7. Select Library tab on left

8. Add the following libraries
<img src = "Images/Tutorial Photos/PlatformIO Setup/bus_io_library.png" />
<img src = "Images/Tutorial Photos/PlatformIO Setup/drv_library.png" />
<img src = "Images/Tutorial Photos/PlatformIO Setup/lsm_library.png" />

9. From the ESP32 folder, copy "firmware-V2.cpp", "utils.cpp", and "utils.h" to the "src" folder in the PlatformIO project. The final file setup should look like this.
<img src = "Images/Tutorial Photos/PlatformIO Setup/file_structure.png" />

10. To push code to the board, push the arrow in the top right (may need to select the drop down and select "Upload")
<img src = "Images/Tutorial Photos/PlatformIO Setup/upload_button.png" />

### Communicating with ESP32 via serial port
This will teach you how to send messages to the ESP32 via the Serial port that will control the haptic motor drivers and the onboard IMU.

#### Initial ESP32 Setup
1. Complete the [PlatformIO Setup](#platformio-setup).
2. Set the user-definable variables in the firmware. The value of the variable `DEVICE_ID` does not matter when using serial communication.

<img src = "Images/Tutorial Photos/PlatformIO Setup/user_defined_variables.png" />

3. In the generated platformio.ini file, set the baud rate with the line "monitor_speed=9600".
<img src = "Images/Tutorial Photos/PlatformIO Setup/set_baud_rate.png" />

4. Connect the ESP32 to your computer via USB and upload the firmware by clicking the arrow button in the top right of the IDE.

#### Example Use
We will use an example message that was used in the [Message Format section](#message-format). Feel free to use other example messages from that section to familiarize yourself with the message structure. Or, be brave and create your own message (just be sure to follow the correct structure!)

##### Turning all drivers on with an effect message
1. Open the serial monitor (Ctrl + Shift + P to open program)
<img src = "Images/Tutorial Photos/PlatformIO Setup/open_serial.png" />

2. Copy the following message by selecting it, right clicking, and selecting copy. In the serial monitor, right click, paste, then press <kbd>Enter</kbd> -> `E,100,43,55,1,123,34,99,2`

2. If the variable `debug` is set to `true`, the following should be the last of what prints to the Serial Monitor:

<img src = "Images/Tutorial Photos/PlatformIO Setup/serial_output.png" />

3. All drivers should now be activated. Driver number 1 should be set to haptic effect # 100, driver number 2 should be set to haptic effect # 43, and so on.

##### Accessing the accelerometer data using an acceleration message (Deprecated on ESP32, no Accelerometer)
1. In the serial monitor, type the following message and then press <kbd>Enter</kbd> (enter it EXACTLY as it appears here): `A,1`

<img src = "Images/Tutorial Photos/Serial Example Use/Serial Accel Message Example.png" />

2. As long as the variable `debug` is set to `true`, the following should print to the Serial Monitor. `outMsg` is the object that is sent to the TCP client. Acceleration data is now being continuously collected.

<img src = "Images/Tutorial Photos/Message Examples/Example Serial Acceleration Message.png" />

3. Now input the message `A,0` or just simply `A` into the Serial Monitor. Notice how the continuous collection of accelerometer data has stopped.

### Communicating with the ESP32 via TCP socket connection
This will teach you how to send messages to the ESP32 via a TCP socket to control the haptic motor drivers and the onboard IMU.

#### Initial PlatformIO Setup
1. Complete the [PlatformIO Setup](#platformio-setup).
2. Set the user-definable variables in the firmware. Be sure to set `DEVICE_ID` to a unique integer [10, 100].

<img src = "Images/Tutorial Photos/PlatformIO Setup/user_defined_variables.png" />

3. Connect the ESP32 to your computer via USB and upload the firmware by clicking the arrow button in the top right of the IDE.

#### Setting up Python
This assumes that you already have Python installed and can successfully run a Python script.
1. Clone this repository (glove-V2) to your local computer
2. Open the repository in your preferred IDE (PyCharm is recommended)
3. Congrats! Python is now ready for use with the haptic glove.

#### Example Use
We will use `glove-demo-single.py` for this example. This is meant as a demonstration of the glove-V2 capabilities so that you can go on and create your own applications using the same methods.

1. After cloning this repository, open `glove-demo-single.py`
2. Ensure the correct parameters are set for the Glove object (`device_id`, `port`, `acceleration`, and `verbose`). Explanations for these parameters are in this Python file
3. The demo script is now ready for use. You can go ahead and run it, or customize the effect numbers that are sent to the glove.

**NOTE:** If you choose to activate the accelerometer on the Arduino (this is the default) then be sure that the `acceleration` property of the glove object is set to `True`. This will turn on continuous transmission of acceleration data until the Python script ends. Be sure that `glove.accel_loop` is set to `False` at the end of this example script. Otherwise, the program will be stuck in a loop and will continue to output acceleration data until the program is manually killed.


# Recommendations for Future Work
## Software Development
### General
Explore both `firmware-V2` and the Python scripts to both:
- Familiarize yourself with the workings of each, and
- Look at and address the various "TODO:" comments that are shrewn throughout.
### VS Code
Install [PlatformIO](https://docs.platformio.org/en/latest/integration/ide/vscode.html#ide-vscode) for VS Code to develop Arduino code. Also look at [this link](https://docs.platformio.org/en/latest/boards/atmelsam/nano_33_iot.html#board-atmelsam-nano-33-iot) to learn how to set up VS Code to use the Nano 33 IoT within PlatformIO.
### Checksum/Parity Check
Implement a checksum to verify the authenticity of each message recieved over TCP Socket
- We ran into some trouble implementing this, so we abandoned our efforts since this is a secondary feature that is not necesary for the design. There is already some rudimentary draft code in `firmware-V2` and `glove.py`
### Implementing Threads
Update `firmware-V2` to utilize threads for each main process (managing WiFi & onboard LED, controlling the haptic motor drivers, and receiving/parsing messages from both Serial and TCP Socket). We have been looking at and prototyping with [Arduino Free RTOS SAMD21](https://github.com/BriscoeTech/Arduino-FreeRTOS-SAMD21/tree/master) for this.
#### Onboard LED state meanings
Make it to where the below table is what happens
|State|Meaning|
--- | --- |
|OFF|Not connected to network|
|BLINKING|Connected to user specified network|
|SOLID|TCP client connected and ready for messages|

### Message Parser
#### Implement custom parser rather than strtok()
Currently, `firmware-V2` uses the built in function `strtok()` to parse received messages. This function has state and remembers the delimeter. Change the parsing process to use a custom parser so that this pipeline is more reliable and does not have state.
#### Make message system more robust
- Sometimes the software freezes if message does not contain instructions for all 8 motors

## Debugging the Arduino using an Atmel-ICE
Look into some surface mounted pins or magnetic pins to access the Arduino's debug pins on the underside of the Arduino. Learn how to use the Atmel-ICE to interface with these pins to debug the Arduino. Refer to [this PlatformIO link](https://docs.platformio.org/en/latest/boards/atmelsam/nano_33_iot.html#board-atmelsam-nano-33-iot) and [this SAM-based Arduino debugging tutorial](https://docs.arduino.cc/tutorials/mkr-wifi-1010/atmel-ice/) for reference for the beginning of your search of how to debug the Nano 33 IoT with the Atmel-ICE.

## Reworking Python Haptic Glove Game & Demo to Work with Glove V2
The lab's glove demos currently only work with V1 of both the glove and Python code. Update these demos to work with the V2 glove and Python code. This will likely require some internal restructuring of the demos themselves.

## PCB Revision
### 5V Step Up Converter
When using battery power for glove V2, a 5V boost/step up converter must be used to provide the Arduino with enough voltage. as of Spring 2024, we are using a [PowerBoost 1000 Basic](https://www.adafruit.com/product/2030?gad_source=1&gclid=Cj0KCQjw0MexBhD3ARIsAEI3WHJGWiqXa6Qvy5UAzQNldZxjR16mb_I9gWrGQy2Cvcb_LnZyqPt9uMoaAlsDEALw_wcB) breakout board from Arduino for this. Make a new PCB revision that includes this boost converter and all required circuitry onto the PCB itself.
