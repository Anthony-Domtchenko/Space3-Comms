#include "dataDisplay.hpp"


void printWod(COMMS_BeaconData_t& receivedWod) {
  Serial.println("---------------------------------------------------------------");
  Serial.print("Beacon Time: ");
  Serial.print(receivedWod.utc_time);
  Serial.print("\r\n");

  Serial.print("CubeSat Identifier: ");
  for (uint8_t c : receivedWod.identifier) {
    Serial.printf("%d", c);
  }
  Serial.print("\r\n");

  //EPS Telemetry
  Serial.printf("Rail 3v3 Voltage: %d\r\n", receivedWod.rail_3v3_voltage);
  Serial.printf("Rail 3v3 Current Ch1: %d\r\n", receivedWod.rail_3v3_current_ch1);
  Serial.printf("Rail 3v3 Current Ch2: %d\r\n", receivedWod.rail_3v3_current_ch2);
  Serial.printf("Rail 5v Voltage: %d\r\n", receivedWod.rail_5v_voltage);
  Serial.printf("Rail 5v Current Ch1: %d\r\n", receivedWod.rail_5v_current_ch1);
  Serial.printf("Rail 5v Current Ch2: %d\r\n", receivedWod.rail_5v_current_ch2);
  Serial.printf("Rail 6v Voltage: %d\r\n", receivedWod.rail_6v_voltage);
  Serial.printf("Rail 6v Current Ch1: %d\r\n", receivedWod.rail_6v_current_ch1);
  Serial.printf("Rail 6v Current Ch2: %d\r\n", receivedWod.rail_6v_current_ch2);
  Serial.printf("Rail 12v Voltage: %d\r\n", receivedWod.rail_12v_voltage);
  Serial.printf("Rail 12v Current Ch1: %d\r\n", receivedWod.rail_12v_current_ch1);
  Serial.printf("Rail 12v Current Ch2: %d\r\n", receivedWod.rail_12v_current_ch2);
  Serial.printf("Battery Voltage: %d\r\n", receivedWod.battery_voltage);
  Serial.printf("System Voltage: %d\r\n", receivedWod.sys_voltage);
  Serial.printf("Battery Current: %d\r\n", receivedWod.battery_current);
  Serial.printf("Battery Temp: %d\r\n", receivedWod.battery_temp);
  Serial.printf("MCU Temp: %d\r\n", receivedWod.mcu_temp);
  Serial.printf("Charger IC Temp: %d\r\n", receivedWod.charger_die_temp);
  Serial.printf("MPPT1 Voltage: %d\r\n", receivedWod.mppt1_voltage);
  Serial.printf("MPPT1 Current: %d\r\n", receivedWod.mppt1_current);
  Serial.printf("MPPT2 Voltage: %d\r\n", receivedWod.mppt2_voltage);
  Serial.printf("MPPT2 Current: %d\r\n", receivedWod.mppt2_current);
  Serial.printf("eFuse States: %d\r\n", receivedWod.eFuse_states);
  Serial.printf("eFuse Faults: %d\r\n", receivedWod.eFuse_faults);
  

  //ADCS Telemetry
  Serial.printf("Roll: %.4f\r\n", receivedWod.roll);
  Serial.printf("Pitch: %.4f\r\n", receivedWod.pitch);
  Serial.printf("Yaw: %.4f\r\n", receivedWod.yaw);
  Serial.printf("Omega X: %.4f\r\n", receivedWod.omega_x);
  Serial.printf("Omega Y: %.4f\r\n", receivedWod.omega_y);
  Serial.printf("Omega Z: %.4f\r\n", receivedWod.omega_z);
  Serial.printf("xRW Speed: %.2f\r\n", receivedWod.x_rw_speed);
  Serial.printf("yRW Speed: %.2f\r\n", receivedWod.y_rw_speed);
  Serial.printf("zRW Speed: %.2f\r\n", receivedWod.z_rw_speed);
  Serial.printf("zRW Speed: %.2f\r\n", receivedWod.z_rw_speed);
  Serial.printf("x Mag Current: %.2f\r\n", receivedWod.x_mag_current);
  Serial.printf("y Mag Current: %.2f\r\n", receivedWod.y_mag_current);
  Serial.printf("z Mag Current: %.2f\r\n", receivedWod.z_mag_current);
  Serial.printf("Detumble Scale: %.2f\r\n", receivedWod.detumble_scale);
  
  // FAULTS
  Serial.printf("EPS Faults: %d\r\n", receivedWod.EPS_Faults);
  Serial.printf("OBC Faults: %d\r\n", receivedWod.OBC_Faults);
  Serial.printf("ADCS Faults: %d\r\n", receivedWod.ADCS_Faults);
  Serial.printf("Payload Faults: %d\r\n", receivedWod.Payload_Faults);
  Serial.printf("Comms Faults: %d\r\n", receivedWod.Comms_Faults);

  Serial.println("---------------------------------------------------------------");
}