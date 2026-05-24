#include "beacon.hpp"
#include "LoRaWan_APP.h"
#include "Arduino.h"

void setup() {
  Serial.begin(115200);
  Mcu.begin(HELTEC_BOARD,SLOW_CLK_TPYE);

  Serial.println();
  Serial.println("Configuring LoRa Transmitter...");
  initLoRa();
}

void loop() {
  delay(5000);
  std::vector<char> msg = {1, 2, 3, 4, 5, 6};
  Serial.println("Sending Packet!");
  std::vector<char> packet = ax25encode(msg, true);
  sendLoRa(packet);
}
