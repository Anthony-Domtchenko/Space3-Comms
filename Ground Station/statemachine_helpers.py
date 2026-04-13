from enum import Enum

# States for the ground_station state machine
class State(Enum):
    IDLE = 0
    TEST_PING = 1
    WOD_DOWNLINK = 2
    SCI_DOWNLINK = 3
    CLEAR_WOD = 4
    EXIT = 5


# Handles the initial user request for the gorund station task to perform
# Returns: Next State for gorund_station state machine
def taskRequest():
    nextState = State.IDLE
    request = input("Select a function:\n"
        "TEST PING\n"
        "WOD DOWNLINK\n"
        "SCI DOWNLINK\n"
        "CLEAR WOD\n"
        "EXIT\n")

    if (request == "TEST PING"):
        nextState = State.TEST_PING
    elif (request == "WOD DOWNLINK"):
        nextState = State.WOD_DOWNLINK
    elif (request == "SCI DOWNLINK"):
        nextState = State.SCI_DOWNLINK
    elif(request == "CLEAR WOD"):
        nextState = State.CLEAR_WOD
    elif(request == "EXIT"):
        nextState = State.EXIT
    else:
        print("Invalid input")
        nextState = State.IDLE

    return nextState