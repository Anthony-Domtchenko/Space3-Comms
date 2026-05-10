#ifndef AX25_HPP
#define AX25_HPP

//--------------------------------------------------------------------------------------------
// File contains functions for encoding and decoding of AX.25 UI Packets
// Please make sure all packets are encoded using ax25.hpp functions to avoid potential errors
// Author: A.Domtchenko   Date: 08.04.2026
//--------------------------------------------------------------------------------------------

#include <cstdint>
#include <vector>
#include <array>

#define FLAG    0x7E
#define ESCAPE  0x7D


// This class is a storage container for incoming AX.25 packets to make processing of information easier
// It should be used after recieveAx25Packet from transmission.hpp
class RxAx25 {
  public:
    // Constructor takes in the raw unbyte-stuffed AX.25 packet and unpacks the data into relevant fields
    RxAx25(std::vector<char>& packet);

    // Getter functions to prevent accidental editing of data fields
    std::array<char,6> getDestAddr();
    uint8_t getDestSSID();
    std::array<char,6> getSourAddr();
    uint8_t getSourSSID();
    std::vector<char> getData();
    std::array<char,2> getFcs();
    std::array<char,2> getCalculatedFcs();
    bool fcsCompare();

  
  private:
    std::array<char,6>  destAddr;
    uint8_t             destSSID;
    std::array<char,6>  sourAddr;
    uint8_t             sourSSID;
    std::vector<char>   data;
    std::array<char,2>  fcs;
    std::array<char,2>  calculatedFcs;
};


// NOTE: addresses are hard coded because we wont be sending to any other satellites but might change if time permits
// Encodes byte data into AX.25 UI format to send to ground station (source address is always satellite)
// Maximum amount of data is 256 bytes
// msgType: "TRUE" for WOD data, "FALSE" for science data
// returns: ON SUCCESS: byte-stuffed ax25 packet
//          ON FAILURE: empty vector
std::vector<char> ax25encode(std::vector<char>& data, bool msgType);

// Calculates AX.25 FCS from input data
std::array<char,2> calculateFcs(std::vector<char>& data);


#endif