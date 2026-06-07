from enum import Enum

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
                   "EXIT TESTING\n")
    
    if (device == "X RW"):
        return 30
    elif (device == "Y RW"):
        return 31
    elif (device == "z RW"):
        return 32
    elif (device == "X MAG"):
        return 33
    elif (device == "Y MAG"):
        return 34      
    elif (device == "Z MAG"):
        return 35
    elif (device == "PAYLOAD"):
        return 36
    elif (device == "CAMERA"):
        return 37
    elif (device == "EXIT TESTING"):
        return 38
    else:
        print("Invalid input")
        return -1