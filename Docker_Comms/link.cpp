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
        if (!handleSciDownlink(client)) {
          Serial.println("ERROR: SCI Downlink Failed");
        }
      }

      else if (linkTask == LINK_CLEAR_WOD) {

      }

      else if (linkTask == LINK_SEND_PARAMS) {
        if (!handleParamsUplink(client)) {
          Serial.println("ERROR: Params Uplink Failed");
        }
      }

      else if (linkTask == TEST_OVERRIDE) {
        if (!handleTestOverride(client)) {
          Serial.println("ERROR: Test Override Failed");
        }
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

  // send ack to OBC for EOF


  sendOBCRequest(WOD_REQUEST_ID);   // Send message to OBC requesting WOD Data
  if (!waitUART()) {                // Sit and wait for response
    return false;
  }                       
  if (!getSendFileInfo(client, true)) {   // Retrieve the File header from the OBC and send it to the ground station
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
      std::vector<char> rawData(msg.payload + 2, msg.payload + msg.length);   // +2 to get rid of index
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

  sendObcAck();                     // Send acknowledgement to OBC for EOF
  return true;
}



bool handleSciDownlink(WiFiClient* client) {
  // -----------------------------------------------------------
  // Almost an exact copy of wod downlink just changed some IDs
  // -----------------------------------------------------------

  sendOBCRequest(SCI_REQUEST_ID);   // Send message to OBC requesting WOD Data
  if (!waitUART()) {                // Sit and wait for response
    return false;
  }                       
  if (!getSendFileInfo(client, false)) {   // Retrieve the File header from the OBC and send it to the ground station
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
        Serial.println("Warning: Bad UART SCI chunk length");
        return false;
      }
      if (msg.id == END_TRANSFER_ID) {
        Serial.println("SCI end of transfer reached");
        break;
      }
      if (msg.id != SCI_CHUNK_ID)
      { 
        Serial.println("Warning: Bad SCI chunk ID received from OBC");
        return false;
      }
      
      // SEND THE WOD CHUNK TO GROUND STATION
      std::vector<char> rawData(msg.payload, msg.payload + msg.length);
      std::vector<char> txPacket = ax25encode(rawData, false);
      if (!sendAx25Packet(client, txPacket)) {
        return false;
      }
    }
    else {
      return false;
    }

    sendObcAck();                   // Send acknowledgement to OBC
  }

  sendObcAck();                     // Send acknowledgement to OBC for EOF
  return true;
}



bool handleParamsUplink(WiFiClient* client) {
  // Send file uplink request to OBC
  // wait Ack
  // get file info from GS and send File info to OBC
  // wait Ack

  // while client connection is open or ack_recieved = false
    // if ack_recieved = true 
      // get chunk from GS and send to OBC
    // else
      // resend previous packet
    // wait for ack
      // if get_ack()
        // ack_recieved = true
        // break
      // else
        // ack_recieved = false

  // send EOF to OBC
  // wait Ack

  sendOBCRequest(SEND_PARAMS_REQUEST_ID);             // Send file uplink request to OBC

  if (!uplinkFileInfo(client)) {                         // get file info from GS and send File info to OBC (also waits for ack)                     
    return false;
  }  

  Serial.println("Sending Chunks to OBC!");
  while(client->connected() || client->available()) {   // loop through and send chunks until TCP connection is ended
    // get next packet
    std::vector<char> ax25packet = recieveAx25Packet(client);
    RxAx25 receivedChunk(ax25packet);
    if (receivedChunk.fcsCompare()) {
      Serial.println("File chunk recieved from GS: FCS is okay");
    }
    else {
      Serial.println("File chunk recieved from GS: FCS is SHIT");
      return false;
    }

    // create UART msg and send to OBC
    std::vector<char> fileChunk = receivedChunk.getData();

    uint8_t indexHighByte = static_cast<uint8_t>(fileChunk[0]);
    uint8_t indexLowByte  = static_cast<uint8_t>(fileChunk[1]);
    uint16_t index = (static_cast<uint16_t>(indexHighByte) << 8) | indexLowByte;

    UART_msg_t msg;
    msg.sof        = UART_SOF;
    msg.id         = SEND_PARAMS_CHUNK_ID;
    msg.length     = fileChunk.size();
    memcpy(msg.payload, fileChunk.data(), fileChunk.size());
    UART_transmit(&Serial2, &msg);
    Serial.printf("Sending Packet to OBC, msg id: %d    length: %d    index: %d\r\n", msg.id, msg.length, index);

    // wait for an ack and resend if required
    int ackCounter = 0;
    while(!getAck()) {
      if (ackCounter == MAX_ACK_RETRIES) {
        Serial.println("Failed to recieve acknowledgement");
        return false;
      }
      UART_transmit(&Serial2, &msg);
      ackCounter++;
    }
  }

  sendEOF();                                          // send EOF to OBC
  int ackCounter = 0;
  while(!getAck()) {                                  // wait Ack
    if (ackCounter == MAX_ACK_RETRIES) {
      Serial.println("Failed to recieve acknowledgement for EOF");
      return false;
    }
    sendEOF();
    ackCounter++;
  }

  return true;
}


bool uplinkFileInfo(WiFiClient* client) {
  // get file info
  std::vector<char> ax25packet = recieveAx25Packet(client);
  RxAx25 receivedFileInfo(ax25packet);
  if (receivedFileInfo.fcsCompare()) {
    Serial.println("File info packet recieved: FCS is okay");
  }
  else {
    return false;
  }

  // create UART msg and send to OBC
  std::vector<char> fileInfo = receivedFileInfo.getData();
  UART_msg_t msg;
  msg.sof        = UART_SOF;
  msg.id         = FILE_INFO_ID;
  msg.length     = fileInfo.size();
  memcpy(msg.payload, fileInfo.data(), fileInfo.size());
  UART_transmit(&Serial2, &msg);
  Serial.println("Sent uplink file info");

  // wait for an ack and resend if required
  int ackCounter = 0;
  while(!getAck()) {
    if (ackCounter == MAX_ACK_RETRIES) {
      Serial.println("Failed to recieve acknowledgement");
      return false;
    }
    UART_transmit(&Serial2, &msg);
    ackCounter++;
  }

  return true;
}



bool handleTestOverride(WiFiClient* client) {
  
  sendOBCRequest(TEST_OVERRIDE_ID);

  // wait for ack
  int ackCounter = 0;
  while(!getAck()) {
    if (ackCounter == MAX_ACK_RETRIES) {
      Serial.println("Failed to recieve acknowledgement");
      return false;
    }
    sendOBCRequest(TEST_OVERRIDE_ID);
    ackCounter++;
  }

  while(true) {
    std::vector<char> ax25packet = recieveAx25Packet(client);
    RxAx25 receivedOverride(ax25packet);
    TEST_OVERRIDE_MSG_t testMsg;

    auto data = receivedOverride.getData();
    if (data.size() == sizeof(TEST_OVERRIDE_MSG_t)) {
        memcpy(&testMsg, data.data(), sizeof(testMsg));
    }
    else {
      Serial.println("Message from ground station incorrect size");
      return false;
    }

    if (receivedOverride.fcsCompare()) {
      Serial.println("Test Override packet recieved: FCS is okay");
    }
    else {
      Serial.println("Test Override packet recieved: FCS is shit, exiting test mode");
      testMsg.device = TEST_EXIT;
    }

    Serial.printf("Sending component override %d request to OBC\r\n", testMsg);
    UART_msg_t msg;
    msg.sof        = UART_SOF;
    msg.id         = TEST_OVERRIDE_ID;
    msg.length     = 1;
    memcpy(msg.payload, &data, sizeof(TEST_OVERRIDE_MSG_t));
    UART_transmit(&Serial2, &msg);

    int ackCounter = 0;
    while(!getAck()) {
      if (ackCounter == MAX_ACK_RETRIES) {
        Serial.println("Failed to recieve acknowledgement");
        return false;
      }
      UART_transmit(&Serial2, &msg);
      ackCounter++;
    }

    if (testMsg.device == TEST_EXIT) {
      break;
    }
  }
}



void sendOBCRequest(uint8_t requestID) {
  UART_msg_t msg;
  msg.sof        = UART_SOF;
  msg.id         = requestID;
  msg.length     = 1;
  msg.payload[0] = requestID;
  UART_transmit(&Serial2, &msg);
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

bool getSendFileInfo(WiFiClient* client, bool wodTrue) {
  // GET THE FILE INFO FROM OBC
  UART_msg_t msg;
  if (UART_receive(&Serial2, &msg, DEFAULT_UART_TIMEOUT_US))
  {
    if (msg.length < 1)
    {
      Serial.println("Warning: Bad file info message length");
      return false;
    }
    if (msg.id != FILE_INFO_ID)
    { 
      Serial.println("Warning: Bad file info ID received from OBC");
      return false;
    }
    
    // SEND THE FILE INFO TO GROUND STATION
    int fileID = msg.payload[0];
    int chunkSize = (msg.payload[1] << 24) | (msg.payload[2] << 16) | (msg.payload[3] << 8) | msg.payload[4];
    int numChunks = (msg.payload[5] << 24) | (msg.payload[6] << 16) | (msg.payload[7] << 8) | msg.payload[8];
    Serial.printf("Transmitting File Info with File ID: %d Chunk Size: %d No. Chunks: %d\r\n", fileID, chunkSize, numChunks);
    std::vector<char> rawData(msg.payload, msg.payload + msg.length);
    std::vector<char> txPacket = ax25encode(rawData, wodTrue);
    if (sendAx25Packet(client, txPacket)) {
      return true;
    }
  }
  return false;
}

bool getAck(void) {
  UART_msg_t msg;
  if (UART_receive(&Serial2, &msg, ACK_WAIT_TIMEOUT_US)) {
    if (msg.length < 1)
    {
      Serial.println("Warning: Bad acknowledgement message length");
      return false;
    }
    if (msg.id != COMMS_ACK_ID)
    { 
      Serial.println("Warning: Bad ACK ID received from OBC");
      return false;
    }
  }
  else {
    Serial.println("ACK: No successful UART Message received");
    return false;
  }
  return true;
}

void sendEOF(void) {
  UART_msg_t msg;
  msg.sof = UART_SOF;
  msg.id  = END_TRANSFER_ID;
  msg.length = 1;
  msg.payload[0] = END_TRANSFER_ID;
  UART_transmit(&Serial2, &msg);
}

