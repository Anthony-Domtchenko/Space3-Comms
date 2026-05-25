#include "link.hpp"


void handleLink(WiFiClient* client) {
  while (client->connected()) {
    if (client->available()) {
      LinkTask linkTask = getTask(client);

      if (linkTask == LINK_WOD_DOWNLINK) {
        handleWodDownlink(client);
      }

      else if (linkTask == LINK_SCI_DOWNLINK) {
        handleSciDownlink(client);
      }

      else if (linkTask == LINK_CLEAR_WOD) {

      }

      else if (linkTask == LINK_SEND_PARAMS) {

      }

      else {
        Serial.println("Something catasrophic has happened if we end up here");
      }

      client->stop();
      Serial.println("Client Disconnected");
    }
  }
}



LinkTask getTask(WiFiClient* client) {
  // Start by recieving the request packet from the ground station
  std::vector<char> packet = recieveAx25Packet(client);
  RxAx25 requestP(packet);
  if (requestP.fcsCompare()) {
    Serial.println("Request packet recieved: FCS is okay");
  }
  else {
    Serial.println("WARNING: FCS of incoming packet does not match calculated");
    return LINK_INVALID;
  }
  if (requestP.getData().size() > 1) {
    Serial.println("Client Request was not valid");
    return LINK_INVALID;
  }

  switch (requestP.getData()[0]) {
    case LINK_WOD_DOWNLINK:
      return LINK_WOD_DOWNLINK;
      break;
    case LINK_SCI_DOWNLINK:
      return LINK_SCI_DOWNLINK;
      break;
    case LINK_CLEAR_WOD:
      return LINK_CLEAR_WOD;
      break;
    case LINK_SEND_PARAMS:
      return LINK_SEND_PARAMS;
      break;
    default:
      Serial.println("Client Request was not valid");
      return LINK_INVALID;
      break;
  }
}



void handleWodDownlink(WiFiClient* client) {
  // Send message to OBC requesting WOD Data
  // while OBC Uart not available
      // delay(1)
  // Receive file info
  // Send Ack to OBC

  // LOOP
    // while OBC Uart not available
      // delay(1)
    // Receive Chunk
    // If transfer end chunk
      // break
    // Send Ack to OBC
    // Send Chunk to GS


  // Send message to OBC requesting WOD Data

}



void handleSciDownlink(WiFiClient* client) {
  Serial.println("Sending SCI Data");
  std::vector<char> sampleData = {1, 0, 0, 0, 1, 1, 0, 0, 0, 1};
  for (int i = 1; i <= 10; i++) {
    sampleData.front() = static_cast<char>(i);
    sampleData.back() = static_cast<char>(i);
    std::vector<char> txPacket = ax25encode(sampleData, false);
    sendAx25Packet(client, txPacket);
    Serial.printf("Sending Packet %d\n", i);
  }
}


