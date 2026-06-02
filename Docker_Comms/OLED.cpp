#include "OLED.hpp"


void initOLED(void) {
  // give power to the screen 3v3 pin
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, LOW);

  display.init();
  Serial.println();
  Serial.println("Configuring OLED Screen...");
}

void bootScreen(void) {
  display.clear();
  char str[30];
  int x = 0;
  int y = 0;
  display.setFont(ArialMT_Plain_24);
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  x = display.width()/2;
  y = display.height()/2 -12;   // -12 as that is half the font height
  sprintf(str,"DOCKER-1");
  display.drawString(x, y, str);
  display.display();
}