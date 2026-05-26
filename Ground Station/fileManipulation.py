from ax25 import *
import csv
import os
import re

# Function breaks up a file of buffered data and returns a list of byte arrays where each entry is a RAW ax25 packet in received order
def extract_frames(raw_data: bytes, frame_char: bytes, escape_char: bytes):
    frames = []
    current_frame = bytearray()
    i = 0

    while i < len(raw_data):
        # Check for the escape character
        if raw_data[i:i+1] == escape_char and i + 1 < len(raw_data):
            # Take the escaped byte literally and skip the escape character
            current_frame.extend(raw_data[i+1:i+2])
            i += 2
        # Check for the frame character
        elif raw_data[i:i+1] == frame_char and len(current_frame) != 0:
            current_frame.extend(raw_data[i:i+1])
            frames.append(bytes(current_frame))
            current_frame.clear()
            i += 1
        else:
            current_frame.append(raw_data[i])
            i += 1

    # Append the last frame if it doesn't end with a delimiter
    if current_frame:
        frames.append(bytes(current_frame))

    return frames



# Function takes in a filename (<name>.csv) and converts satellite data stored in "rawData.txt" to usable csv format
# Format: "DESTINATION ADDRESS", "DESTINATION SSID", "SOURCE ADDRESS", "SOURCE SSID", "INFORMATION FIELD (HEX)", "RECIEVED CRC-16", "CALCULATED CRC-16"
# where each row is a seperate ax25 packet
def processAx25Data(filename):
    with open('rawData.txt', "rb") as f_in, open(filename, 'w', newline='', encoding='utf-8') as f_out:
        # Split raw data into AX25 packets by flag delimeters
        content = f_in.read()
        delimiter = b'\x7E'
        escape = b'\x7d'
        ax25Chunks = extract_frames(content, delimiter, escape)

        # Unstuff each packet and write relevant data to a CSV file
        writer = csv.writer(f_out)
        header = ["DESTINATION ADDRESS", "DESTINATION SSID", "SOURCE ADDRESS", "SOURCE SSID", "INFORMATION FIELD (HEX)", "RECIEVED CRC-16", "CALCULATED CRC-16"]
        writer.writerow(header)
        for i in ax25Chunks:
            decodedPacket = ax25decode(i)
            row = [decodedPacket.destAddr, decodedPacket.destSSID, decodedPacket.sourAddr, decodedPacket.sourSSID, decodedPacket.data.hex(), decodedPacket.fcs.hex(), decodedPacket.calculatedFcs.hex()]
            writer.writerow(row)

    print("Data Processing Complete and Stored to CSV")



# Coverts Raw WOD Data into a csv with a header containing the received File Info and subsequent rows with each sensor value
# HEADER FORMAT: FileId, ChunkSize, NumChunks
###
# DATA FORMAT: See LOGGING_Record_t struct in OBC code
def processWodData(filename):
    with open('rawData.txt', "rb") as f_in, open(filename, 'w', newline='', encoding='utf-8') as f_out:
        # Split raw data into AX25 packets by flag delimeters
        content = f_in.read()
        delimiter = b'\x7E'
        escape = b'\x7d'
        ax25Chunks = extract_frames(content, delimiter, escape)

        # Write the format of the file header
        writer = csv.writer(f_out)
        fileHeader = ["FileId", "ChunkSize", "NumChunks"]
        writer.writerow(fileHeader)

        # Write the file header data
        firstPacket = ax25decode(ax25Chunks[0])
        fileID = firstPacket.data[0]
        chunkSize = int.from_bytes(firstPacket.data[1:5], byteorder='big')
        numChunks = int.from_bytes(firstPacket.data[5:9], byteorder='big')
        writer.writerow([fileID, chunkSize, numChunks])
        writer.writerow([])  # Writes a blank row

        # Write the format of the rows
        rowHeader = ['Sequence', 'Year', 'Month', 'Day', 'Hours', 'Minutes', 'Seconds', '3v3 Voltage', '3v3 Current Ch1', '3v3 Current Ch2',
                     '5V Voltage', '5V Current Ch1', '5V Current Ch2', '6V Voltage', '6V Current Ch1', '12V Voltage', '12V Current Ch1',
                     '12V Current Ch2', 'MPPT1 Voltage', 'MPPT1 Current', 'MPPT2 Voltage', 'MPPT2 Current', 'Bat Voltage', 'Bat Current',
                     'Bat Temp', 'MCU Temp', 'Roll', 'Pitch', 'Yaw', 'xRw Speed', 'yRw Speed', 'zRw Speed', 'xMag Current', 'yMag Current',
                     'zMag Current', 'OBC Faults']
        writer.writerow(rowHeader)

        # Write each row making sure to skip the first packet which contains the header data
        firstPacketFlag = 0
        for i in ax25Chunks:
            if (firstPacketFlag == 0):
                firstPacketFlag += 1
                continue

            decodedPacket = ax25decode(i)

            sequence        = int.from_bytes(decodedPacket.data[0:8], byteorder='big')

            year            = int.from_bytes(decodedPacket.data[8:10], byteorder='big')
            month           = int.from_bytes(decodedPacket.data[10:11], byteorder='big')
            day             = int.from_bytes(decodedPacket.data[11:12], byteorder='big')
            hours           = int.from_bytes(decodedPacket.data[12:13], byteorder='big')
            minutes         = int.from_bytes(decodedPacket.data[13:14], byteorder='big')
            seconds         = int.from_bytes(decodedPacket.data[14:15], byteorder='big')

            rail3v3Volt     = int.from_bytes(decodedPacket.data[15:17], byteorder='big')
            rail3v3Curr1    = int.from_bytes(decodedPacket.data[17:19], byteorder='big')
            rail3v3Curr2    = int.from_bytes(decodedPacket.data[19:21], byteorder='big')

            rail5VVolt      = int.from_bytes(decodedPacket.data[21:23], byteorder='big')
            rail5VCurr1     = int.from_bytes(decodedPacket.data[23:25], byteorder='big')
            rail5VCurr2     = int.from_bytes(decodedPacket.data[25:27], byteorder='big')

            rail6vVolt      = int.from_bytes(decodedPacket.data[27:29], byteorder='big')
            rail6vCurr1     = int.from_bytes(decodedPacket.data[29:31], byteorder='big')

            rail12VVolt     = int.from_bytes(decodedPacket.data[31:33], byteorder='big')
            rail12VCurr1    = int.from_bytes(decodedPacket.data[33:35], byteorder='big')
            rail12VCurr2    = int.from_bytes(decodedPacket.data[35:37], byteorder='big')

            mppt1Volt       = int.from_bytes(decodedPacket.data[37:39], byteorder='big')
            mppt1Curr       = int.from_bytes(decodedPacket.data[39:41], byteorder='big')
            mppt2Volt       = int.from_bytes(decodedPacket.data[41:43], byteorder='big')
            mppt2Curr       = int.from_bytes(decodedPacket.data[43:45], byteorder='big')

            batVolt         = int.from_bytes(decodedPacket.data[45:47], byteorder='big')
            batCurr         = int.from_bytes(decodedPacket.data[47:49], byteorder='big')
            batTemp         = int.from_bytes(decodedPacket.data[49:51], byteorder='big')
            mcuTemp         = int.from_bytes(decodedPacket.data[51:53], byteorder='big')

            roll            = int.from_bytes(decodedPacket.data[53:55], byteorder='big', signed=True)
            pitch           = int.from_bytes(decodedPacket.data[55:57], byteorder='big', signed=True)
            yaw             = int.from_bytes(decodedPacket.data[57:59], byteorder='big', signed=True)

            xRw             = int.from_bytes(decodedPacket.data[59:61], byteorder='big', signed=True)
            yRw             = int.from_bytes(decodedPacket.data[61:63], byteorder='big', signed=True)
            zRw             = int.from_bytes(decodedPacket.data[63:65], byteorder='big', signed=True)

            xMag            = int.from_bytes(decodedPacket.data[65:67], byteorder='big', signed=True)
            yMag            = int.from_bytes(decodedPacket.data[67:69], byteorder='big', signed=True)
            zMag            = int.from_bytes(decodedPacket.data[69:71], byteorder='big', signed=True)

            obcFaults       = int.from_bytes(decodedPacket.data[71:73], byteorder='big')

            row = [sequence, year, month, day, hours, minutes, seconds, rail3v3Volt, rail3v3Curr1, rail3v3Curr2, rail5VVolt, rail5VCurr1, rail5VCurr2,
                   rail6vVolt, rail6vCurr1, rail12VVolt, rail12VCurr1, rail12VCurr2, mppt1Volt, mppt1Curr, mppt2Volt, mppt2Curr, batVolt, batCurr,
                   batTemp, mcuTemp, roll, pitch, yaw, xRw, yRw, zRw, xMag, yMag, zMag, obcFaults]
            writer.writerow(row)

    print("Data Processing Complete and Stored to CSV")




def deleteRawDataFile():
    # Delete the rawData file
    if os.path.exists('rawData.txt'):
        os.remove('rawData.txt')
        print("Raw Data file deleted successfully.")
    else:
        print("The file does not exist.")
    return