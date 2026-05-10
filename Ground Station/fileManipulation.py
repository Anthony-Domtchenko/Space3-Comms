from ax25 import *
import time


#with open('rawData.txt', "rb") as f_in, open('WODdata.txt', 'wb') as f_out:
with open('rawData.txt', "rb") as f_in:
    content = f_in.read()
    delimiter = b'\x7E\x7E'
    ax25Chunks = content.split(delimiter)
    print(len(ax25Chunks), len(ax25Chunks[1]))
    #print("RAW DATA:", ax25Chunks[0].hex(' '))

    iterator = 1
    for i in ax25Chunks:
        if (iterator == 1):
            newBytes = i + b'\x7E'
            decodedPacket = ax25decode(newBytes)
            print(decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(' '), decodedPacket.fcs.hex(' '))
        elif (iterator == len(ax25Chunks)):
            newBytes = b'\x7E' + i
            decodedPacket = ax25decode(newBytes)
            print(decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(' '), decodedPacket.fcs.hex(' '))
        else:
            newBytes = b'\x7E' + i + b'\x7E'
            decodedPacket = ax25decode(newBytes)
            print(decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(' '), decodedPacket.fcs.hex(' '))

        iterator += 1
    