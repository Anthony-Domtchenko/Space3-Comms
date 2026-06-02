from ctypes import *
import math

class WodPacket(Structure):
    _pack_ = 1
    _fields_ = [
        ('year', c_uint16),
        ('month', c_uint8),
        ('day', c_uint8),
        ('hours', c_uint8),
        ('minutes', c_uint8),
        ('seconds', c_uint8),

        ('raw_3v3_voltage', c_uint16),
        ('raw_3v3_current_ch1', c_uint16),
        ('raw_3v3_current_ch2', c_uint16),

        ('raw_5v_voltage', c_uint16),
        ('raw_5v_current_ch1', c_uint16),
        ('raw_5v_current_ch2', c_uint16),

        ('raw_6v_voltage', c_uint16),
        ('raw_6v_current_ch1', c_uint16),

        ('raw_12v_voltage', c_uint16),
        ('raw_12v_current_ch1', c_uint16),
        ('raw_12v_current_ch2', c_uint16),

        ('mppt1_voltage', c_uint16),
        ('mppt1_current', c_uint16),
        ('mppt2_voltage', c_uint16),
        ('mppt2_current', c_uint16),

        ('raw_battery_voltage', c_uint16),
        ('raw_battery_current', c_uint16),
        ('battery_temp', c_uint16),
        ('mcu_temp', c_uint16),

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

        ('EPS_Faults', c_uint16),
        ('OBC_Faults', c_uint16),
        ('ADCS_Faults', c_uint16),
        ('Payload_Faults', c_uint16),
        ('Comms_Faults', c_uint16),
    ]

    @property
    def rail_3v3_voltage(self):
        return self.raw_3v3_voltage * 0.001555

    @property
    def rail_3v3_current_ch1(self):
        return self.raw_3v3_current_ch1 * 0.0008954

    @property
    def rail_3v3_current_ch2(self):
        return self.raw_3v3_current_ch2 * 0.0008954

    @property
    def rail_5v_voltage(self):
        return self.raw_5v_voltage * 0.00161132812

    @property
    def rail_5v_current_ch1(self):
        return self.raw_5v_current_ch1 * 0.0012397

    @property
    def rail_5v_current_ch2(self):
        return self.raw_5v_current_ch2 * 0.0012397

    @property
    def rail_6v_voltage(self):
        return self.raw_6v_voltage * 0.00161132812

    @property
    def rail_6v_current_ch1(self):
        return self.raw_6v_current_ch1 * 0.003663

    @property
    def rail_12v_voltage(self):
        return self.raw_12v_voltage * 0.006498

    @property
    def rail_12v_current_ch1(self):
        return self.raw_12v_current_ch1 * 0.00080586

    @property
    def rail_12v_current_ch2(self):
        return self.raw_12v_current_ch2 * 0.00080586

    @property
    def battery_voltage(self):
        return self.raw_battery_voltage * 0.001

    @property
    def battery_current(self):
        return self.raw_battery_current * 0.001
    
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