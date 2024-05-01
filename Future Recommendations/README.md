# Recommendations for Future Work
## Software Development
### VS Code
Install [PlatformIO](https://docs.platformio.org/en/latest/integration/ide/vscode.html#ide-vscode) for VS Code to develop Arduino code
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
TODO
#### Make message system more robust
- Sometimes the software freezes if message does not contain instructions for all 8 motors

## Debugging the Arduino using an Atmel-ICE
TODO

## Reworking Python Haptic Glove Game & Demo to Work with Glove V2
TODO

## PCB Revision
### 5V Step Up Converter
TODO
