#ifndef OLED_HPP
#define OLED_HPP

#include "HT_SSD1306Wire.h"
#include "Arduino.h"
#include <Wire.h>

static SSD1306Wire  display(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED); // addr , freq , i2c group , resolution , rst

void initOLED(void);
void bootScreen(void);

#endif