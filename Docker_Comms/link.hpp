#ifndef LINK_HPP
#define LINK_HPP

//--------------------------------------------------------------------------------------------
// File contains functions for handling groundstation link
// Author: A.Domtchenko   Date: 25.05.2026
//--------------------------------------------------------------------------------------------

#include <vector>
#include <cstdint>
#include <WiFi.h>
#include <WiFiAP.h>
#include "uart.h"
#include "ax25.hpp"
#include "Arduino.h"
#include "transmission.hpp"


//-------------DEFINES------------------------------------------------------------------------
#define FILE_INFO_ID    0x66
#define COMMS_ACK_ID    0x68
#define END_TRANSFER_ID 0x70

#define WOD_REQUEST_ID  0x67
#define WOD_RECORD_ID   0x69

#define SCI_REQUEST_ID  0x14  
#define SCI_CHUNK_ID    0x69

#define SEND_PARAMS_REQUEST_ID  0x13
#define SEND_PARAMS_CHUNK_ID    0x69

#define TEST_OVERRIDE_ID        0x11  // Check and update this

#define UART_WAIT_TIMEOUT_US  2000000
#define ACK_WAIT_TIMEOUT_US   20000
#define MAX_ACK_RETRIES       10


//-------------Typedefs and Enums-------------------------------------------------------------
typedef enum{
  LINK_INVALID = -1,
  LINK_WOD_DOWNLINK,
  LINK_SCI_DOWNLINK,
  LINK_CLEAR_WOD,
  LINK_SEND_PARAMS,
  TEST_OVERRIDE
}LinkTask;

// Serial2 is reserved for OBC-COMMS UART connection
extern HardwareSerial Serial2;


//-------------Function Prototypes------------------------------------------------------------
// decides what actions need to be performed when a link is established
void handleLink(WiFiClient* client);

// recieve the task the groundstation would like the satellite to perform
LinkTask getTask(WiFiClient* client);

//Handlers for each LinkTask
bool handleWodDownlink(WiFiClient* client);
bool handleSciDownlink(WiFiClient* client);

bool handleParamsUplink(WiFiClient* client);
bool uplinkFileInfo(WiFiClient* client);

bool handleTestOverride(WiFiClient* client);

void sendOBCRequest(uint8_t requestID);
bool waitUART(void);
void sendObcAck(void);
bool getSendFileInfo(WiFiClient* client, bool wodTrue);
bool getAck(void);
void sendEOF(void);


#endif