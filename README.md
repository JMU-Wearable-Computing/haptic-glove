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
TODO

### Arduino Libraries
Included within repo:  
1. Adafruit_NeoPixel.h
2. Adafruit_DRV2605.h

## Communicating with Arduino Nano

TODO

### Message format
Messages follows the format: /n01/n02/n03/n04  
nXX is a number of length 3 between 0 and 255.
Each segment of the message correspondes to the strength of a specific motor.
Where n01 controls motor 1, n02 controls motor 2 and so on.
