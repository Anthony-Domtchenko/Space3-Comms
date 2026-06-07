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
  y = display.height()/2 -24;
  sprintf(str,"BEACON");
  display.drawString(x, y, str);
  x = display.width()/2;
  y = display.height()/2;
  sprintf(str,"RECEIVER");
  display.drawString(x, y, str);
  display.display();
}

void newRxScreen(COMMS_BeaconData_t& receivedWod, int rssi) {
  display.clear();
  char str[50];
  int x = 0;
  int y = 0;

  display.setFont(ArialMT_Plain_16);
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  x = display.width()/2;
  y = 8;   // 8 as that is half the font height
  sprintf(str,"Packet Recieved:");
  display.drawString(x, y, str);

  display.setFont(ArialMT_Plain_10);
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  x = display.width()/2;
  y = 28;   // 16 as that is height of header
  sprintf(str,"%s", receivedWod.utc_time);
  display.drawString(x, y, str);

  display.setFont(ArialMT_Plain_10);
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  x = display.width()/2;
  y = 38;   // 16 as that is height of header
  sprintf(str,"RSSI: %d    Bat Volt: %.2f", rssi, float(receivedWod.battery_voltage) * 0.001);
  display.drawString(x, y, str);

  display.setFont(ArialMT_Plain_10);
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  x = display.width()/2;
  y = 48;   // 16 as that is height of header
  sprintf(str,"R:%.2f  P:%.2f  Y:%.2f", receivedWod.roll, receivedWod.pitch, receivedWod.yaw);
  display.drawString(x, y, str);

  display.display();
}