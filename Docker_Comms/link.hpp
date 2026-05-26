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
#define WOD_INFO_ID     0x66
#define WOD_REQUEST_ID  0x67
#define COMMS_ACK_ID    0x68
#define WOD_RECORD_ID   0x69
#define END_TRANSFER_ID 0x70

#define UART_WAIT_TIMEOUT_US 2000000


//-------------Typedefs and Enums-------------------------------------------------------------
typedef enum{
  LINK_INVALID = -1,
  LINK_WOD_DOWNLINK,
  LINK_SCI_DOWNLINK,
  LINK_CLEAR_WOD,
  LINK_SEND_PARAMS
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
void sendWodRequest(void);
bool getSendFileInfo(WiFiClient* client);

void handleSciDownlink(WiFiClient* client);

bool waitUART(void);  // timeout occurs if program waits longer than UART_WAIT_TIMEOUT_US mircroseconds
void sendObcAck(void);


#endif