from ax25 import *
import csv

# Function takes in a filename (<name>.csv) and converts satellite data stored in "rawData.txt" to usable csv format
# Current format: "DESTINATION ADDRESS", "DESTINATION SSID", "SOURCE ADDRESS", "SOURCE SSID", "INFORMATION FIELD (HEX)", "RECIEVED CRC-16", "CALCULATED CRC-16"
# where each row is a seperate ax25 packet
def processRawData(filename):
    with open('rawData.txt', "rb") as f_in, open(filename, 'w', newline='', encoding='utf-8') as f_out:
        # Split raw data into AX25 packets by flag delimeters
        content = f_in.read()
        delimiter = b'\x7E\x7E'
        ax25Chunks = content.split(delimiter)

        # Unstuff each packet and write relevant data to a CSV file
        writer = csv.writer(f_out)
        header = ["DESTINATION ADDRESS", "DESTINATION SSID", "SOURCE ADDRESS", "SOURCE SSID", "INFORMATION FIELD (HEX)", "RECIEVED CRC-16", "CALCULATED CRC-16"]
        writer.writerow(header)
        iterator = 1
        for i in ax25Chunks:
            if (iterator == 1):
                newBytes = i + b'\x7E'
                decodedPacket = ax25decode(newBytes)
                row = [decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(), decodedPacket.fcs.hex(), decodedPacket.calculatedFcs.hex()]
                writer.writerow(row)

            elif (iterator == len(ax25Chunks)):
                newBytes = b'\x7E' + i
                decodedPacket = ax25decode(newBytes)
                row = [decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(), decodedPacket.fcs.hex(), decodedPacket.calculatedFcs.hex()]
                writer.writerow(row)
                
            else:
                newBytes = b'\x7E' + i + b'\x7E'
                decodedPacket = ax25decode(newBytes)
                row = [decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(), decodedPacket.fcs.hex(), decodedPacket.calculatedFcs.hex()]
                writer.writerow(row)               

            iterator += 1

    print("Data Processing Complete and Stored to CSV")
    return