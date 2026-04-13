#include "transmission.hpp"
#include <WiFi.h>
#include <vector>


std::vector<char> recieveAx25Packet(WiFiClient* client){
  std::vector<char> rawData;
  char byte = client->read();
  char escapeFlag = 0;

  // Check that packet reading is synchronise (first byte should be a flag)
  if (byte == FLAG) {
    // Make sure to append that first flag
    rawData.push_back(byte);

    int itCount = 1;
    while(true) {
      if (itCount > 500)
      {
        Serial.println("Error in recieveAx25Packet No return FLAG found");
        std::vector<char> error;
        return error;
      }

      byte = client->read();
      if (escapeFlag == 0 && byte == ESCAPE) {
        escapeFlag = 1;
        continue;
      }
      else if (escapeFlag == 0 && byte == FLAG) {
        rawData.push_back(byte);
        break;
      }
      else if (escapeFlag == 1) {
        rawData.push_back(byte);
        escapeFlag = 0;
      }
      else {
        // (escapeFlag == 0 && byte is something random)
        rawData.push_back(byte);
      }
      itCount++;
    }
  }
  else {
    Serial.println("ERROR: Recieved packet is out of sync!!");
    // NOTE: should probably add some resyncing code at some point where it just drops bytes until a FLAG is found
  }

  return rawData;
}


int sendAx25Packet(WiFiClient* client, std::vector<char>& packet){
  int bombo = 1;
  return bombo;
}


