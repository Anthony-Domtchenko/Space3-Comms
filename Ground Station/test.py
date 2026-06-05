import socket
from statemachine_helpers import *
from satClient import satClient
from fileManipulation import *
from fileUplink import *

WOD_FOLDER = 'WOD Data'
SCI_FOLDER = 'Science Data'
HIST_FOLDER = 'Histograms'
csv_path = 'results.csv'

serialisedFile = load_settings(EXPERIMENT_SETTINGS_PATH)
packetsToSend = make_packets(serialisedFile)

print(packetsToSend[0].hex())