#ifndef BEACON_HPP
#define BEACON_HPP

//--------------------------------------------------------------------------------------------
// File contains functions for transmitting beacon sent from OBC using LoRa
// Author: A.Domtchenko   Date: 24.05.2026
//--------------------------------------------------------------------------------------------

#include <vector>
#include <cstdint>
#include "uart.h"
#include "ax25.hpp"
#include "LoRaWan_APP.h"
#include "Arduino.h"


#define RF_FREQUENCY                                915000000 // Hz
#define TX_OUTPUT_POWER                             5         // dBm
#define LORA_BANDWIDTH                              0         // [0: 125 kHz,
                                                              //  1: 250 kHz,
                                                              //  2: 500 kHz,
                                                              //  3: Reserved]
#define LORA_SPREADING_FACTOR                       7         // [SF7..SF12]
#define LORA_CODINGRATE                             1         // [1: 4/5,
                                                              //  2: 4/6,
                                                              //  3: 4/7,
                                                              //  4: 4/8]
#define LORA_PREAMBLE_LENGTH                        8         // Same for Tx and Rx
#define LORA_SYMBOL_TIMEOUT                         0         // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON                  false
#define LORA_IQ_INVERSION_ON                        false
#define RX_TIMEOUT_VALUE                            1000


#define BEACON_MSG_ID            0x65
#define BEACON_TIME_STRING_BYTES 32
#define CUBESAT_IDENTIFIER_BYTES 6
#define BEACON_MSG_DATA_BYTES    72


// Serial2 is reserved for OBC-COMMS UART connection
extern HardwareSerial Serial2; 

typedef struct __attribute__((packed)) {
    char utc_time[BEACON_TIME_STRING_BYTES];
    uint8_t identifier[CUBESAT_IDENTIFIER_BYTES];

    //EPS Telemetry
    uint16_t rail_3v3_voltage;
    uint16_t rail_3v3_current_ch1;
    uint16_t rail_3v3_current_ch2;
    uint16_t rail_5v_voltage;
    uint16_t rail_5v_current_ch1;
    uint16_t rail_5v_current_ch2;
    uint16_t rail_6v_voltage;
    uint16_t rail_6v_current_ch1;
    uint16_t rail_6v_current_ch2;
    uint16_t rail_12v_voltage;
    uint16_t rail_12v_current_ch1;
    uint16_t rail_12v_current_ch2;
    uint16_t battery_voltage;
    uint16_t sys_voltage;
    uint16_t battery_current;
    uint8_t  battery_temp;
    uint16_t mcu_temp;
    uint8_t  charger_die_temp;
    uint16_t mppt1_voltage;
    uint16_t mppt2_voltage;
    uint16_t mppt1_current;
    uint16_t mppt2_current;
    uint8_t  eFuse_states;
    uint8_t  eFuse_faults;

    //ADCS Telemetry
    float    roll;
    float    pitch;
    float    yaw;
    float    omega_x;
    float    omega_y;
    float    omega_z;
    float    x_rw_speed;
    float    y_rw_speed;
    float    z_rw_speed;
    float    x_mag_current;
    float    y_mag_current;
    float    z_mag_current;

    float    x_mag_field_sense;
    float    y_mag_field_sense;
    float    z_mag_field_sense;
    float    x_mag_field_filt;
    float    y_mag_field_filt;
    float    z_mag_field_filt;
    
    float    detumble_scale;
    
    uint16_t EPS_Faults;
    uint16_t OBC_Faults;
    uint16_t ADCS_Faults;
    uint16_t Payload_Faults;
    uint16_t Comms_Faults;
}COMMS_BeaconData_t;

typedef enum {
    COMMS_IDLE,
    COMMS_WOD_DOWNLINK, 
    COMMS_PAYLOAD_DOWNLINK,
}COMMS_state_t;


typedef enum {
    DOWNLINK_IDLE,
    DOWNLINK_SEND_INFO,
    DOWNLINK_SEND_CHUNK,
    DOWNLINK_WAIT_ACK,
    DOWNLINK_COMPLETE,
    DOWNLINK_ERROR
}COMMS_downlinkState_t;

typedef struct {
    COMMS_downlinkState_t state;
    bool downlink_active;
    uint8_t ack_retries;
    uint32_t end_ptr;
    uint32_t num_chunks;
}COMMS_fileHandler_t;



typedef struct{
    uint32_t beacon_tick;
    COMMS_fileHandler_t wod_handler;
    COMMS_fileHandler_t results_handler;
}COMMS_Handler_t;


// initialises the LoRa chip
void initLoRa(void);

// handles the sending of a beacon from the OBC. returns 1 on success, 0 if no beacon present
bool handleOBCBeacon(void);

// checks the beacon data to see if its a valid format. returns 1 if valid
bool checkMessage(UART_msg_t* msg);

// sends the LoRa packet of ax25 encoded data
void sendLoRa(std::vector<char>& data);

// Radio event callbacks
void OnTxDone(void);
void OnTxTimeout(void);


#endif