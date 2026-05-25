from ax25 import *
import csv
import os
import re

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
# Current format: "DESTINATION ADDRESS", "DESTINATION SSID", "SOURCE ADDRESS", "SOURCE SSID", "INFORMATION FIELD (HEX)", "RECIEVED CRC-16", "CALCULATED CRC-16"
# where each row is a seperate ax25 packet
def processRawData(filename):
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
    # Delete the rawData file
    if os.path.exists('rawData.txt'):
        os.remove('rawData.txt')
        print("Raw Data file deleted successfully.")
    else:
        print("The file does not exist.")
    return