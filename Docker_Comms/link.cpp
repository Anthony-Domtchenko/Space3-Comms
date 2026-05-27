#include "link.hpp"


void handleLink(WiFiClient* client) {
  while (client->connected()) {
    if (client->available()) {
      LinkTask linkTask = getTask(client);

      if (linkTask == LINK_WOD_DOWNLINK) {
        if (!handleWodDownlink(client)) {
          Serial.println("ERROR: WOD Downlink Failed");
        }
      }

      else if (linkTask == LINK_SCI_DOWNLINK) {
        handleSciDownlink(client);
      }

      else if (linkTask == LINK_CLEAR_WOD) {

      }

      else if (linkTask == LINK_SEND_PARAMS) {

      }

      else {
        Serial.println("Ground Station Request Failed");
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



bool handleWodDownlink(WiFiClient* client) {
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
    // Send Chunk to GS
    // Send Ack to OBC


  sendWodRequest();                 // Send message to OBC requesting WOD Data
  if (!waitUART()) {                // Sit and wait for response
    return false;
  }                       
  if (!getSendFileInfo(client)) {   // Retrieve the File header from the OBC and send it to the ground station
    return false;
  }
  sendObcAck();                     // Send acknowledgement to OBC

  while(true) {                     // Loop through receiving and transmitting WOD data until EOF message

    if (!waitUART()) {              // Sit and wait for response
      return false;
    } 

    // RECEIVE THE WOD CHUNK FROM OBC
    UART_msg_t msg;
    if (UART_receive(&Serial2, &msg, DEFAULT_UART_TIMEOUT_US))
    {
      if (msg.length < 1)
      {
        Serial.println("Warning: Bad UART WOD message length");
        return false;
      }
      if (msg.id == END_TRANSFER_ID) {
        Serial.println("WOD end of transfer reached");
        break;
      }
      if (msg.id != WOD_RECORD_ID)
      { 
        Serial.println("Warning: Bad WOD chunk ID received from OBC");
        return false;
      }
      
      // SEND THE WOD CHUNK TO GROUND STATION
      std::vector<char> rawData(msg.payload, msg.payload + msg.length);
      std::vector<char> txPacket = ax25encode(rawData, true);
      if (!sendAx25Packet(client, txPacket)) {
        return false;
      }
    }
    else {
      return false;
    }

    sendObcAck();                   // Send acknowledgement to OBC
  }

  return true;
}

void sendWodRequest(void) {
  UART_msg_t msg;
  msg.sof        = UART_SOF;
  msg.id         = WOD_REQUEST_ID;
  msg.length     = 1;
  msg.payload[0] = WOD_REQUEST_ID;
  UART_transmit(&Serial2, &msg);
}

bool getSendFileInfo(WiFiClient* client) {
  // GET THE FILE INFO FROM OBC
  UART_msg_t msg;
  if (UART_receive(&Serial2, &msg, DEFAULT_UART_TIMEOUT_US))
  {
    if (msg.length < 1)
    {
      Serial.println("Warning: Bad file info message length");
      return false;
    }
    if (msg.id != WOD_INFO_ID)
    { 
      Serial.println("Warning: Bad file info ID received from OBC");
      return false;
    }
    
    // SEND THE FILE INFO TO GROUND STATION
    int fileID = msg.payload[0];
    int chunkSize = (msg.payload[1] << 24) | (msg.payload[2] << 16) | (msg.payload[3] << 8) | msg.payload[4];
    int numChunks = (msg.payload[5] << 24) | (msg.payload[6] << 16) | (msg.payload[7] << 8) | msg.payload[8];
    Serial.printf("Transmitting WOD file with File ID: %d Chunk Size: %d No. Chunks: %d\r\n", fileID, chunkSize, numChunks);
    std::vector<char> rawData(msg.payload, msg.payload + msg.length);
    std::vector<char> txPacket = ax25encode(rawData, true);
    if (sendAx25Packet(client, txPacket)) {
      return true;
    }
  }
  return false;
}



void handleSciDownlink(WiFiClient* client) {
  Serial.println("Sending SCI Data");
  std::vector<char> sampleData = {1, 0, 0, 0, 1, 1, 0, 0, 0, 1};
  for (int i = 1; i <= 10; i++) {
    sampleData.front() = static_cast<char>(i);
    sampleData.back() = static_cast<char>(i);
    std::vector<char> txPacket = ax25encode(sampleData, false);
    sendAx25Packet(client, txPacket);
    Serial.printf("Sending Packet %d\r\n", i);
  }
}




bool waitUART(void) {
  // Sit and wait for UART from OBC to arrive
  int waitTime_us = 0;
  while (!Serial2.available()) {
    if (waitTime_us > UART_WAIT_TIMEOUT_US) {
      Serial.println("ERROR: UART timed out waiting for OBC");
      return false;
    }
    delayMicroseconds(1);
    waitTime_us++;
  }
  return true;
}

void sendObcAck(void) {
  UART_msg_t msg;
  msg.sof = UART_SOF;
  msg.id  = COMMS_ACK_ID;
  msg.length = 1;
  msg.payload[0] = COMMS_ACK_ID;
  UART_transmit(&Serial2, &msg);
}

