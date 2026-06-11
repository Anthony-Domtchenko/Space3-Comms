import socket
from statemachine_helpers import *
from satClient import satClient
from fileManipulation import *
from fileUplink import *

WOD_FOLDER = 'WOD Data'
SCI_FOLDER = 'Science Data'
HIST_FOLDER = 'Histograms'
csv_path = 'results.csv'

a = "ab_c".split()
b = "ab bc".split()

print(len(a))
print(len(b[0]))

print(a)
print(b)