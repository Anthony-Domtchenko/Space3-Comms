import socket
from statemachine_helpers import *
from satClient import satClient
from fileManipulation import *

WOD_FOLDER = 'WOD Data'
SCI_FOLDER = 'Science Data'

csv_relative_path = f"./{WOD_FOLDER}/WODdata.csv"  # This is a stupid line of code
processWodData(WOD_FOLDER, 'WODdata.csv')
plotWodData(csv_relative_path, WOD_FOLDER)