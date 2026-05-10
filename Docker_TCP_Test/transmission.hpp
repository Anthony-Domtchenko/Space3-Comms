#ifndef TRANSMISSION_HPP
#define TRANSMISSION_HPP

//--------------------------------------------------------------------------------------------
// File contains functions for transmitting and recieving AX.25 UI Packets
// Please make sure all packets are encoded using ax25.hpp functions to avoid potential errors
// Author: A.Domtchenko   Date: 08.04.2026
//--------------------------------------------------------------------------------------------

#include <vector>
#include <Wifi.h>

#define FLAG    0x7E
#define ESCAPE  0x7D


// Function recieves an AX25 UI packet from another source and returns it as a vector
// It assumes the packet is byte-stuffed using the FLAG and ESCAPE characters
// Function stops reading when it reaches the last FLAG
// INPUT: pointer to a connected WiFi client
// RETURNS:
//        ON SUCCESS: unbyte-stuffed ax25 packet as vector w/flags
//        ON Failure: empty vector and print message to serial monitor
std::vector<char> recieveAx25Packet(WiFiClient* client);


// Function sends an AX25 UI packet to a client connected to the ESP32
// It assumes the packet is byte-stuffed using the FLAG and ESCAPE characters and in AX.25 UI format
// Function stops sending when it reaches the last FLAG
// INPUT: AX.25 UI Frame
// RETURNS:
//        1: On Success
//        0: On Failure
int sendAx25Packet(WiFiClient* client, std::vector<char>& packet);


#endif