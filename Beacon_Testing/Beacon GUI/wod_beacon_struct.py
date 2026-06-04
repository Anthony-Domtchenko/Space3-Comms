from ctypes import *
import math
import ctypes

BEACON_TIME_STRING_BYTES = 32
CUBESAT_IDENTIFIER_BYTES = 6

class BeaconPacket(Structure):
    _pack_ = 1
    _fields_ = [
        # Strings / identifiers
        ('raw_utc_time', c_char * BEACON_TIME_STRING_BYTES),
        ('raw_identifier', c_uint8 * CUBESAT_IDENTIFIER_BYTES),

        # EPS Telemetry
        ('raw_rail_3v3_voltage', c_uint16),
        ('raw_rail_3v3_current_ch1', c_uint16),
        ('raw_rail_3v3_current_ch2', c_uint16),

        ('raw_rail_5v_voltage', c_uint16),
        ('raw_rail_5v_current_ch1', c_uint16),
        ('raw_rail_5v_current_ch2', c_uint16),

        ('raw_rail_6v_voltage', c_uint16),
        ('raw_rail_6v_current_ch1', c_uint16),
        ('raw_rail_6v_current_ch2', c_uint16),

        ('raw_rail_12v_voltage', c_uint16),
        ('raw_rail_12v_current_ch1', c_uint16),
        ('raw_rail_12v_current_ch2', c_uint16),

        ('raw_battery_voltage', c_uint16),
        ('raw_sys_voltage', c_uint16),
        ('raw_battery_current', c_uint16),
        ('battery_temp', c_uint8),
        ('mcu_temp', c_uint16),
        ('charger_die_temp', c_uint8),

        ('raw_mppt1_voltage', c_uint16),
        ('raw_mppt2_voltage', c_uint16),
        ('raw_mppt1_current', c_uint16),
        ('raw_mppt2_current', c_uint16),

        ('eFuse_states', c_uint8),
        ('eFuse_faults', c_uint8),

        # ADCS Telemetry
        ('roll', c_float),
        ('pitch', c_float),
        ('yaw', c_float),
        ('raw_omega_x', c_float),
        ('raw_omega_y', c_float),
        ('raw_omega_z', c_float),
        ('raw_x_rw_speed', c_float),
        ('raw_y_rw_speed', c_float),
        ('raw_z_rw_speed', c_float),
        ('x_mag_current', c_float),
        ('y_mag_current', c_float),
        ('z_mag_current', c_float),
        ('detumble_scale', c_float),

        # Subsystem Faults
        ('EPS_Faults', c_uint16),
        ('OBC_Faults', c_uint16),
        ('ADCS_Faults', c_uint16),
        ('Payload_Faults', c_uint16),
        ('Comms_Faults', c_uint16),
    ]

    @property
    def utc_time(self):
        return self.raw_utc_time.decode('ascii').rstrip('\0')

    @property
    def identifier(self):
        return bytes(self.raw_identifier).decode('ascii').rstrip('\0')

    @property
    def rail_3v3_voltage(self):
        return self.raw_rail_3v3_voltage * 0.001555

    @property
    def rail_3v3_current_ch1(self):
        return self.raw_rail_3v3_current_ch1 * 0.0008954

    @property
    def rail_3v3_current_ch2(self):
        return self.raw_rail_3v3_current_ch2 * 0.0008954

    @property
    def rail_5v_voltage(self):
        return self.raw_rail_5v_voltage * 0.00161132812

    @property
    def rail_5v_current_ch1(self):
        return self.raw_rail_5v_current_ch1 * 0.0012397

    @property
    def rail_5v_current_ch2(self):
        return self.raw_rail_5v_current_ch2 * 0.0012397

    @property
    def rail_6v_voltage(self):
        return self.raw_rail_6v_voltage * 0.00161132812

    @property
    def rail_6v_current_ch1(self):
        return self.raw_rail_6v_current_ch1 * 0.003663

    @property
    def rail_6v_current_ch2(self):
        return self.raw_rail_6v_current_ch2 * 0.003663

    @property
    def rail_12v_voltage(self):
        return self.raw_rail_12v_voltage * 0.006498

    @property
    def rail_12v_current_ch1(self):
        return self.raw_rail_12v_current_ch1 * 0.00080586

    @property
    def rail_12v_current_ch2(self):
        return self.raw_rail_12v_current_ch2 * 0.00080586

    @property
    def battery_voltage(self):
        return self.raw_battery_voltage * 0.001

    @property
    def sys_voltage(self):
        return self.raw_sys_voltage * 0.001

    @property
    def battery_current(self):
        return ctypes.c_int16(self.raw_battery_current).value * 0.001
    
    @property
    def omega_x(self):
        return self.raw_omega_x * 30.0 / math.pi    # converts rad/s to rpm
    
    @property
    def omega_y(self):
        return self.raw_omega_y * 30.0 / math.pi    # converts rad/s to rpm
    
    @property
    def omega_z(self):
        return self.raw_omega_z * 30.0 / math.pi    # converts rad/s to rpm
    
    @property
    def x_rw_speed(self):
        return self.raw_x_rw_speed / (2.0 * math.pi)    # converts rad/s to rps
    
    @property
    def y_rw_speed(self):
        return self.raw_y_rw_speed / (2.0 * math.pi)    # converts rad/s to rps
    
    @property
    def z_rw_speed(self):
        return self.raw_z_rw_speed / (2.0 * math.pi)    # converts rad/s to rps
    
    @property
    def mppt1_voltage(self):
        return self.raw_mppt1_voltage * 0.001
    
    @property
    def mppt2_voltage(self):
        return self.raw_mppt2_voltage * 0.001
    
    @property
    def mppt1_current(self):
        return self.raw_mppt1_current * 0.001
    
    @property
    def mppt2_current(self):
        return self.raw_mppt2_current * 0.001