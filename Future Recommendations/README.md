# Recommendations for Future Work
## Software Development
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
Look into some surface mounted pins or magnetic pins to access the Arduino's debug pins on the underside of the Arduino. Learn how to use the Atmel-ICE to interface with these pins to debug the Arduino. Refer to [this link](https://docs.platformio.org/en/latest/boards/atmelsam/nano_33_iot.html#board-atmelsam-nano-33-iot) for reference for the beginning of your search of how to debug the Nano 33 IoT with the Atmel-ICE.

## Reworking Python Haptic Glove Game & Demo to Work with Glove V2
The lab's glove demos currently only work with V1 of both the glove and Python code. Update these demos to work with the V2 glove and Python code. This will likely require some internal restructuring of the demos themselves.

## PCB Revision
### 5V Step Up Converter
When using battery power for glove V2, a 5V boost/step up converter must be used to provide the Arduino with enough voltage. as of Spring 2024, we are using a [PowerBoost 1000 Basic]() breakout board from Arduino. Make a new PCB revision to include this boost converter and all required circuitry onto the PCB itself.
