import socket
from statemachine_helpers import *
from satClient import satClient
from fileManipulation import *


currState = State.IDLE
nextState = State.IDLE

while(1):
    currState = nextState

    match currState:
        case State.IDLE:
            nextState = taskRequest()

        case State.TEST_PING:
            client = satClient()
            if (client.connectToSat()):
                client.testPing()
            client.closeClient()

            nextState = State.IDLE

        case State.WOD_DOWNLINK:
            client = satClient()
            if (client.connectToSat()):
                client.wodDownlink()
            client.closeClient()
            processRawData('WODdata.csv')

            nextState = State.IDLE

        case State.SCI_DOWNLINK:
            client = satClient()
            if (client.connectToSat()):
                client.sciDownlink()
            client.closeClient()
            processRawData('SCIdata.csv')

            nextState = State.IDLE

        case State.CLEAR_WOD:
            print("CLEAR WOD OH YEAH\n")
            nextState = State.IDLE

        case State.SEND_PARAMS:
            print("SEND PARAMS OH YEAH\n")
            nextState = State.IDLE

        case State.EXIT:
            print("Exiting...\n")
            break
        
        case _:
            print("Current State took on a strange value\n")
            nextState = State.IDLE