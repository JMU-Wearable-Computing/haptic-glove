#include <Wire.h>
#include "Adafruit_DRV2605.h"

Adafruit_DRV2605 drv1;
Adafruit_DRV2605 drv2;
#define TCAADDR 0x70

// Select which driver to talk to
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  Serial.println("DRV test");
  tcaselect(0);
  drv1.begin();
    
  // I2C trigger by sending 'go' command 
  drv1.setMode(DRV2605_MODE_INTTRIG); // default, internal trigger when sending GO command

  drv1.selectLibrary(1);
  drv1.setWaveform(0, 84);  // ramp up medium 1, see datasheet part 11.2
  drv1.setWaveform(1, 1);  // strong click 100%, see datasheet part 11.2
  drv1.setWaveform(2, 0);  // end of waveforms

  tcaselect(1);
  drv2.begin();
    
  // I2C trigger by sending 'go' command 
  drv2.setMode(DRV2605_MODE_INTTRIG); // default, internal trigger when sending GO command

  drv2.selectLibrary(1);
  drv2.setWaveform(0, 84);  // ramp up medium 1, see datasheet part 11.2
  drv2.setWaveform(1, 1);  // strong click 100%, see datasheet part 11.2
  drv2.setWaveform(2, 0);  // end of waveforms
}

void loop() {
    tcaselect(0);
    drv1.go();
    delay(1000);

    tcaselect(1);
    drv2.go();
    delay(1000);
}
