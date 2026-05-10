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



std::vector<char> ax25encode(std::vector<char>& data, bool msgType) {

  std::vector<char> encodedPacket;
  encodedPacket.reserve(300);         // this just prevents 1 million vector resizings as data is pushed back

  // NOTE: All non data parts of the AX25 UI Frame are hard coded and I dont bother with byte stuffing because I know none of the values
  //       are FLAG or ESCAPE characters (Yes its a dirty solution but idc)

  // Add starting flag
  encodedPacket.push_back(FLAG);

  // Add destination Address
  encodedPacket.push_back(0x8E); // 'G'
  encodedPacket.push_back(0xA4); // 'R'
  encodedPacket.push_back(0x9E); // 'O'
  encodedPacket.push_back(0xAA); // 'U'
  encodedPacket.push_back(0x9C); // 'N'
  encodedPacket.push_back(0x88); // 'D'
  if (msgType == true) {
    encodedPacket.push_back(0xFC); // SSID = 0b1110 for WOD Data
  }
  else {
    encodedPacket.push_back(0xFE); // SSID = 0b1111 for Science Data
  }

  // Add source Address
  encodedPacket.push_back(0x88); // 'D'
  encodedPacket.push_back(0x9E); // 'O'
  encodedPacket.push_back(0x86); // 'C'
  encodedPacket.push_back(0x96); // 'K'
  encodedPacket.push_back(0x8A); // 'E'
  encodedPacket.push_back(0xA4); // 'R'
  encodedPacket.push_back(0xF7); // SSID = 0b1011 (11 in decimal) cos spacecraft

  // Add control field
  encodedPacket.push_back(0x03);

  // Add protocol id
  encodedPacket.push_back(0xf0);

  // Add Data by looping through and adding an escape byte before every FLAG or ESCAPE character
  for (const auto& val : data) {
    if (val == FLAG || val == ESCAPE) {
      encodedPacket.push_back(ESCAPE);
      encodedPacket.push_back(val);
    }
    else {
      encodedPacket.push_back(val);
    }
  }

  // Add fcs
  // NOTE: Currently hard coded but will implement actual FCS later down the line (will also need to be byte stuffed)
  encodedPacket.push_back(0x11);
  encodedPacket.push_back(0x11);

  // Add finishing flag
  encodedPacket.push_back(FLAG);

  return encodedPacket;
}



