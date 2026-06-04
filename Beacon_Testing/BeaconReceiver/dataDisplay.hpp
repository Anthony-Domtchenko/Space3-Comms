#ifndef DATADISPLAY_HPP
#define DATADISPLAY_HPP

#include <cstdint>
#include <cstring>
#include <vector>
#include <array>
#include "Arduino.h"
#include "ax25.hpp"



#define CUBESAT_IDENTIFIER "DOCKER"
#define CUBESAT_IDENTIFIER_BYTES 6
#define BEACON_TIME_STRING_BYTES 32

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

    // Faults 
    uint16_t EPS_Faults;
    uint16_t OBC_Faults;
    uint16_t ADCS_Faults;
    uint16_t Payload_Faults;
    uint16_t Comms_Faults;
}COMMS_BeaconData_t;



void printWod(COMMS_BeaconData_t& receivedWod);

#endif