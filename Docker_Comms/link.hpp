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


typedef enum{
  LINK_INVALID = -1,
  LINK_WOD_DOWNLINK,
  LINK_SCI_DOWNLINK,
  LINK_CLEAR_WOD,
  LINK_SEND_PARAMS
}LinkTask;

// Serial2 is reserved for OBC-COMMS UART connection
extern HardwareSerial Serial2;



// decides what actions need to be performed when a link is established
void handleLink(WiFiClient* client);

// recieve the task the groundstation would like the satellite to perform
LinkTask getTask(WiFiClient* client);

//Handlers for each LinkTask
void handleWodDownlink(WiFiClient* client);
void handleSciDownlink(WiFiClient* client);


#endif