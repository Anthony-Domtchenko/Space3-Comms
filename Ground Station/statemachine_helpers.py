from enum import Enum, auto
from ctypes import *
import ctypes

# States for the ground_station state machine
class State(Enum):
    IDLE = 0
    TEST_PING = 1
    WOD_DOWNLINK = 2
    SCI_DOWNLINK = 3
    CLEAR_WOD = 4
    SEND_PARAMS = 5
    TEST_OVERRIDE = 6
    EXIT = 7


class OverrideDeviceID(Enum):
    TEST_X_RW       = 0x31
    TEST_Y_RW       = auto()
    TEST_Z_RW       = auto()
    TEST_X_MAG      = auto()
    TEST_Y_MAG      = auto()
    TEST_Z_MAG      = auto()
    TEST_PAYLOAD    = auto()
    TEST_CAMERA     = auto()
    EFUSE_ADCS      = auto()
    EFUSE_PAYLOAD   = auto()
    TEST_EXIT       = auto()


class DeviceMsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('device', c_uint8),
        ('magnitude', c_float),
    ]


# Handles the initial user request for the gorund station task to perform
# Returns: Next State for gorund_station state machine
def taskRequest():
    nextState = State.IDLE
    request = input("Select a function:\n"
        "TEST PING\n"
        "WOD DOWNLINK\n"
        "SCI DOWNLINK\n"
        "CLEAR WOD\n"
        "SEND PARAMS\n"
        "TEST OVERRIDE\n"
        "EXIT\n")

    if (request == "TEST PING"):
        nextState = State.TEST_PING
    elif (request == "WOD DOWNLINK"):
        nextState = State.WOD_DOWNLINK
    elif (request == "SCI DOWNLINK"):
        nextState = State.SCI_DOWNLINK
    elif(request == "CLEAR WOD"):
        nextState = State.CLEAR_WOD
    elif(request == "SEND PARAMS"):
        nextState = State.SEND_PARAMS
    elif(request == "TEST OVERRIDE"):
        nextState = State.TEST_OVERRIDE
    elif(request == "EXIT"):
        nextState = State.EXIT
    else:
        print("Invalid input")
        nextState = State.IDLE

    return nextState


def getOverride() -> DeviceMsg:
    device = input("What device would you like to test?\n"
                   "xRW <rpm>\n"
                   "yRW <rpm>\n"
                   "zRW <rpm>\n"
                   "xMAG <rpm>\n"
                   "yMAG <rpm>\n"
                   "zMAG <rpm>\n"
                   "PAYLOAD\n"
                   "CAMERA\n"
                   "EFUSE_ADCS\n"
                   "EFUSE_PAYLOAD\n"
                   "EXIT_TESTING\n").split(' ')
    
    msg = DeviceMsg()

    if (len(msg) > 1 and validFloat(msg[1])):
        msg.magnitude = ctypes.c_float(float(msg[1]))

        if (device[0] == "xRW"):
            msg.device = OverrideDeviceID.TEST_X_RW
            return msg
        elif (device[0] == "yRW"):
            msg.device = OverrideDeviceID.TEST_Y_RW
            return msg
        elif (device[0] == "zRW"):
            msg.device = OverrideDeviceID.TEST_Z_RW
            return msg
        elif (device[0] == "xMAG"):
            msg.device = OverrideDeviceID.TEST_X_MAG
            return msg
        elif (device[0] == "yMAG"):
            msg.device = OverrideDeviceID.TEST_Y_MAG
            return msg 
        elif (device[0] == "zMAG"):
            msg.device = OverrideDeviceID.TEST_Z_MAG
            return msg
        else:
            print("Invalid input")
            msg.device = 255
            return msg
    
    elif (device[0] == "PAYLOAD"):
        msg.device = OverrideDeviceID.TEST_PAYLOAD
        return msg
    elif (device[0] == "CAMERA"):
        msg.device = OverrideDeviceID.TEST_CAMERA
        return msg
    elif (device[0] == "EFUSE_ADCS"):
        msg.device = OverrideDeviceID.EFUSE_ADCS
        return msg
    elif (device[0] == "EFUSE_PAYLOAD"):
        msg.device = OverrideDeviceID.EFUSE_PAYLOAD
        return msg
    elif (device[0] == "EXIT_TESTING"):
        msg.device = OverrideDeviceID.TEST_EXIT
        return msg
    else:
        print("Invalid input")
        msg.device = 255
        return msg
    

def validFloat(value: str) -> bool:
    try:
        convertedValue = ctypes.c_float(float(value))
    except ValueError:
        print(f"Error: '{value}' cannot be parsed into a float.")
        return False
    return True