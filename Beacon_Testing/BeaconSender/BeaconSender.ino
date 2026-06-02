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

int iterator = 0;

void loop() {
  delay(10000);

  COMMS_BeaconData_t dummyData{};
  snprintf(
    dummyData.utc_time,
    BEACON_TIME_STRING_BYTES,
    "%04u-%02u-%02u %02u:%02u:%02u UTC",
    1,
    2,
    3,
    4,
    5,
    iterator
  );
  dummyData.battery_voltage = iterator + 1;
  dummyData.roll = float(iterator) + 0.3;
  dummyData.pitch = float(iterator) + 0.6;
  dummyData.yaw = float(iterator) + 0.9;

  const char* start = reinterpret_cast<const char*>(&dummyData);
  std::vector<char> msg(start, start + sizeof(COMMS_BeaconData_t));

  Serial.println("Sending Packet!");
  std::vector<char> packet = ax25encode(msg, true);
  sendLoRa(packet);

  iterator++;
}
