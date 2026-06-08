from enum import Enum, auto

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


def getOverride():
    device = input("What device would you like to test?\n"
                   "X RW\n"
                   "Y RW\n"
                   "Z RW\n"
                   "X MAG\n"
                   "Y MAG\n"
                   "Z MAG\n"
                   "PAYLOAD\n"
                   "CAMERA\n"
                   "EFUSE ADCS\n"
                   "EFUSE PAYLOAD\n"
                   "EXIT TESTING\n")
    
    if (device == "X RW"):
        return OverrideDeviceID.TEST_X_RW
    elif (device == "Y RW"):
        return OverrideDeviceID.TEST_Y_RW
    elif (device == "z RW"):
        return OverrideDeviceID.TEST_Z_RW
    elif (device == "X MAG"):
        return OverrideDeviceID.TEST_X_MAG
    elif (device == "Y MAG"):
        return OverrideDeviceID.TEST_Y_MAG    
    elif (device == "Z MAG"):
        return OverrideDeviceID.TEST_Z_MAG
    elif (device == "PAYLOAD"):
        return OverrideDeviceID.TEST_PAYLOAD
    elif (device == "CAMERA"):
        return OverrideDeviceID.TEST_CAMERA
    elif (device == "EFUSE ADCS"):
        return OverrideDeviceID.EFUSE_ADCS
    elif (device == "EFUSE PAYLOAD"):
        return OverrideDeviceID.EFUSE_PAYLOAD
    elif (device == "EXIT TESTING"):
        return OverrideDeviceID.TEST_EXIT
    else:
        print("Invalid input")
        return -1