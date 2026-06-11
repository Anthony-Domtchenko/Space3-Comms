import socket
from statemachine_helpers import *
from satClient import satClient
from fileManipulation import *

WOD_FOLDER = 'WOD Data'
SCI_FOLDER = 'Science Data'
HIST_FOLDER = 'Histograms'


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
            processAx25Data(WOD_FOLDER, 'WODax25.csv')
            processWodData(WOD_FOLDER, 'WODdata.csv')
            csv_relative_path = f"./{WOD_FOLDER}/WODdata.csv"  # This is a stupid line of code
            plotWodData(csv_relative_path, WOD_FOLDER)
            #deleteRawDataFile()

            nextState = State.IDLE

        case State.SCI_DOWNLINK:
            client = satClient()
            if (client.connectToSat()):
                client.sciDownlink()
            client.closeClient()
            processAx25Data(SCI_FOLDER, 'SCIAx25data.csv')
            processSciData(SCI_FOLDER, 'SCIAx25data.csv')
            csv_relative_path = f"./{SCI_FOLDER}/SCIAx25data.csv"  # This is a stupid line of code
            save_histograms(csv_relative_path, HIST_FOLDER)
            #deleteRawDataFile()

            nextState = State.IDLE

        case State.CLEAR_WOD:
            print("CLEAR WOD OH YEAH\n")
            nextState = State.IDLE

        case State.SEND_PARAMS:
            client = satClient()
            if (client.connectToSat()):
                client.sendParams()
            client.closeClient()

            nextState = State.IDLE

        case State.TEST_OVERRIDE:
            # Send TEST OVERRIDE REQUEST TO SAT
            client = satClient()
            if (client.connectToSat()):
                client.sendTestRequest()
            else:
                nextState = State.IDLE
                continue
            
            msg = getOverride()
            # stay in Test mode until EXIT is called
            while(msg.device != OverrideDeviceID.TEST_EXIT.value):
                if (msg.device != 255):
                    # valid device
                    client.sendTestOverride(msg)
                msg = getOverride()
            
            # Exit test mode
            client.sendTestOverride(msg)
            client.closeClient()
            nextState = State.IDLE


        case State.EXIT:
            print("Exiting...\n")
            break
        
        case _:
            print("Current State took on a strange value\n")
            nextState = State.IDLE