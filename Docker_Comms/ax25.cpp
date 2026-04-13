#include "ax25.hpp"
#include <array>
#include <vector>

//--------------------------------------------------------------------------------------------
RxAx25::RxAx25(std::vector<char>& packet) {

  for (uint8_t i=0; i < destAddr.size(); i++) {
    char shiftByte = packet[i+1] >> 1;
    destAddr[i] = shiftByte;
  }

  destSSID = (packet[7] >> 1) & 0b1111;

  for (uint8_t i=0; i < sourAddr.size(); i++) {
    char shiftByte = packet[i+8] >> 1;
    sourAddr[i] = shiftByte;
  }

  sourSSID = (packet[14] >> 1) & 0b1111;

  data.assign(packet.begin() + 17, packet.end() - 3);

  for (uint8_t i=0; i < fcs.size(); i++) {
    fcs[i] = packet[packet.size()-3+i];
  }
}


std::array<char,6> RxAx25::getDestAddr() {
  return destAddr;
}

uint8_t RxAx25::getDestSSID() {
  return destSSID;
}

std::array<char,6> RxAx25::getSourAddr() {
  return sourAddr;
}

uint8_t RxAx25::getSourSSID() {
  return sourSSID;
}

std::vector<char> RxAx25::getData() {
  return data;
}

std::array<char,2> RxAx25::getFcs() {
  return fcs;
}
//--------------------------------------------------------------------------------------------




