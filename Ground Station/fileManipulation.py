from ax25 import *
from wod_downlink_struct import *
import csv
import os
import struct
import pandas as pd
import matplotlib.pyplot as plt
import cv2 as cv


# Results file binary schema (must match serialiseResults() in obcMessageHandler.cpp)
NUM_SERVOS          = 6
CAM_W, CAM_H        = 640, 480
BYTES_PER_HISTOGRAM = CAM_W * CAM_H // 8  # 38400
RESULT_TIMESTEPS    = 150
HIST_ROWS, HIST_BYTES = 150, 38_400


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
def processAx25Data(foldername, filename):

    os.makedirs(foldername, exist_ok=True)
    save_path = os.path.join(foldername, filename)

    with open('rawData.txt', "rb") as f_in, open(save_path, 'w', newline='', encoding='utf-8') as f_out:
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

    print("Raw Data Processing Complete and Stored to CSV")



# Coverts Raw WOD Data into a csv with a header containing the received File Info and subsequent rows with each sensor value
# HEADER FORMAT: FileId, ChunkSize, NumChunks
###
# DATA FORMAT: See LOGGING_Record_t struct in OBC code
def processWodData(foldername, filename):

    os.makedirs(foldername, exist_ok=True)
    save_path = os.path.join(foldername, filename)

    with open('rawData.txt', "rb") as f_in, open(save_path, 'w', newline='', encoding='utf-8') as f_out:
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
        rowHeader = ['Year', 'Month', 'Day', 'Hours', 'Minutes', 'Seconds', '3v3 Voltage', '3v3 Current Ch1', '3v3 Current Ch2',
                     '5V Voltage', '5V Current Ch1', '5V Current Ch2', '6V Voltage', '6V Current Ch1', '12V Voltage', '12V Current Ch1',
                     '12V Current Ch2', 'MPPT1 Voltage', 'MPPT1 Current', 'MPPT2 Voltage', 'MPPT2 Current', 'Bat Voltage', 'Bat Current',
                     'Bat Temp', 'MCU Temp', 'Roll', 'Pitch', 'Yaw', 'omegaX', 'omegaY', 'omegaZ', 'xRw Speed', 'yRw Speed', 'zRw Speed',
                     'xMag Current', 'yMag Current', 'zMag Current', 'Detumble Scale', 'EPS Faults', 'OBC Faults', 'ADCS Faults',
                     'Payload Faults', 'Comms Faults']
        writer.writerow(rowHeader)

        # Write each row making sure to skip the first packet which contains the header data
        firstPacketFlag = 0
        for i in ax25Chunks:
            if (firstPacketFlag == 0):
                firstPacketFlag += 1
                continue

            decodedPacket = ax25decode(i)

            if (decodedPacket.fcs != decodedPacket.calculatedFcs):
                continue

            wod = WodPacket.from_buffer_copy(decodedPacket.data)

            row = [wod.year, wod.month, wod.day, wod.hours, wod.minutes, wod.seconds, wod.rail_3v3_voltage, wod.rail_3v3_current_ch1, wod.rail_12v_current_ch2,
                   wod.rail_5v_voltage, wod.rail_5v_current_ch1, wod.rail_5v_current_ch2, wod.rail_6v_voltage, wod.rail_6v_current_ch1, wod.rail_12v_voltage,
                   wod.rail_12v_current_ch1, wod.rail_12v_current_ch2, wod.mppt1_voltage, wod.mppt1_current, wod.mppt2_voltage, wod.mppt2_current,
                   wod.battery_voltage, wod.battery_current, wod.battery_temp, wod.mcu_temp, wod.roll, wod.pitch, wod.yaw, wod.omega_x, wod.omega_y, wod.omega_z,
                   wod.x_rw_speed, wod.y_rw_speed, wod.z_rw_speed, wod.x_mag_current, wod.y_mag_current, wod.z_mag_current, wod.detumble_scale, wod.EPS_Faults,
                   wod.OBC_Faults, wod.ADCS_Faults, wod.Payload_Faults, wod.Comms_Faults]
            writer.writerow(row)

    print("WOD Data Processing Complete and Stored to CSV")



# Produces a bunch of plots from the WOD Data csv file for analysis
def plotWodData(csv_path, save_folder):

    os.makedirs(save_folder, exist_ok=True)

    df = pd.read_csv(csv_path, skiprows=3)  # skip header rows

    
    df['UTC_Time'] = pd.to_datetime(
        {
            'year': df['Year'],
            'month': df['Month'],
            'day': df['Day'],
            'hour': df['Hours'],
            'minute': df['Minutes'],
            'second': df['Seconds']
        },
        utc=True,
    )
    time = df['UTC_Time']

    # Define groups
    groups = {
        'Voltages (V)': ['3v3 Voltage', '5V Voltage', '6V Voltage', '12V Voltage', 'MPPT1 Voltage', 'MPPT2 Voltage', 'Bat Voltage', 'Sys Voltage'],
        'Currents (A)': ['3v3 Current Ch1', '3v3 Current Ch2', '5V Current Ch1', '5V Current Ch2', '6V Current Ch1', '6V Current Ch2', '12V Current Ch1', '12V Current Ch2', 'MPPT1 Current', 'MPPT2 Current', 'Bat Current'],
        'Temperatures (C)': ['Bat Temp', 'MCU Temp'],
        'Sat Angles (Rad)': ['Roll', 'Pitch', 'Yaw'],
        'Sat Angluar Speeds (rpm)': ['omegaX', 'omegaY', 'omegaZ'],
        'Reaction Wheel Speeds (rps)': ['xRw Speed', 'yRw Speed', 'zRw Speed'],
        'Magnetorquer Currents (A)': ['xMag Current', 'yMag Current', 'zMag Current']
    }

    for group_name, columns in groups.items():
        plt.figure(figsize=(12,6))
        for col in columns:
            if col in df.columns:
                plt.plot(time, df[col], label=col)
        plt.xlabel('UTC Time')
        plt.ylabel(group_name)
        plt.title(group_name + ' vs Time')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(save_folder, f'{group_name.replace(" ", "_")}.png'))
        plt.close()  # Close the figure to free memory



# Coverts Raw SCI Data into a csv with a the results histogram
def processSciData(foldername, filename):

    os.makedirs(foldername, exist_ok=True)
    save_path = os.path.join(foldername, filename)

    rawByteStream = b''

    with open('rawData.txt', "rb") as f_in, open(save_path, 'w', newline='', encoding='utf-8') as f_out:
        # Split raw data into AX25 packets by flag delimeters
        content = f_in.read()
        delimiter = b'\x7E'
        escape = b'\x7d'
        ax25Chunks = extract_frames(content, delimiter, escape)

        # extract the data from each ax25 packet ignoring the first row which cntains the file info
        firstPacketFlag = 0
        for i in ax25Chunks:
            if (firstPacketFlag == 0):
                firstPacketFlag += 1
                continue

            decodedPacket = ax25decode(i)
            index = int.from_bytes(decodedPacket.data[0:2], byteorder='little')
            data = decodedPacket.data[2:]       # remove the index from the data

            if (decodedPacket.fcs != decodedPacket.calculatedFcs):
                print(f"packet {index} is corrupted, appending zeros")
                rawByteStream += bytes(len(data))
                continue
            else:
                rawByteStream += data

    print(f"Received {len(rawByteStream)} bytes total. Decoding...")
    output_csv_path = f"./{foldername}/{filename}"
    decode_results(rawByteStream, output_csv_path)



def decode_results(stream: bytes, output_csv_path: str):
    """
    Decode the binary results stream back to CSV format matching results.csv.

    Binary schema (must match serialiseResults() in obcMessageHandler.cpp):
      150 x 6 floats  — servo angles (rows 0-149)
      150 x 3 floats  — camera position (rows 150-299)
      150 x 3 floats  — camera attitude (rows 300-449)
      150 x 38400 bytes — event histogram as packed bits (rows 450-599, hex strings)
    """
    offset = 0
    rows = []

    def read_float() -> float:
        nonlocal offset
        val = struct.unpack_from('<f', stream, offset)[0]
        offset += 4
        return val

    # Servo angles: 150 rows x 6 floats
    for _ in range(RESULT_TIMESTEPS):
        row = [f"{read_float():.6f}" for _ in range(NUM_SERVOS)]
        rows.append(row)

    # Camera position: 150 rows x 3 floats
    for _ in range(RESULT_TIMESTEPS):
        row = [f"{read_float():.6f}" for _ in range(3)]
        rows.append(row)

    # Camera attitude: 150 rows x 3 floats
    for _ in range(RESULT_TIMESTEPS):
        row = [f"{read_float():.6f}" for _ in range(3)]
        rows.append(row)

    # Histogram: 150 rows x 38400 bytes as hex string
    for _ in range(RESULT_TIMESTEPS):
        chunk = stream[offset : offset + BYTES_PER_HISTOGRAM]
        offset += BYTES_PER_HISTOGRAM
        rows.append([chunk.hex()])

    with open(output_csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)

    print(f"Decoded results written to '{output_csv_path}' ({len(rows)} rows)")



def save_histograms(csv_path, save_folder):

    os.makedirs(save_folder, exist_ok=True)

    df = pd.read_csv(csv_path, skiprows= RESULT_TIMESTEPS*3, header=None)

    # Convert histogram data to image for visualisation
    # idk what the histograms are lol



        


def deleteRawDataFile():
    # Delete the rawData file
    if os.path.exists('rawData.txt'):
        os.remove('rawData.txt')
        print("Raw Data file deleted successfully.")
    else:
        print("The file does not exist.")
    return