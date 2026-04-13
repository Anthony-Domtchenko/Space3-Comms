# FILE contains functions to transform data in and out of AX.25 UI format
# https://docs.google.com/spreadsheets/d/1yypI_psGWz_DphJZmaF0-jHVkYakinVdNz3ul18nx5U/edit?usp=sharing

from typing import Literal
from dataclasses import dataclass

# Standard bytes in messages
FLAG = b'\x7E'
ESCAPE = b'\x7D'
# NOTE: should add END_TRANSMISSION that gets escaped or use zero length dat packet?


@dataclass
class ax25info:
    destAddr: str = 'xxxxxx'
    destSSID: int = 0
    sourAddr: str = 'xxxxxx'
    sourSSID: int = 0
    data: bytes = b'\x00'
    fcs: bytes = b'\x11\x11'


# NOTE: need to add FCS implementation
# NOTE: addresses are hard coded because we wont be sending to any other satellites but might change if time permits
# Encodes byte data into AX.25 UI format to send to satellite (source address is always ground sation)
# Maximum amount of data is 256 bytes
# msgType: "wod" for WOD data, "science" for science data
# returns: ON SUCCESS: ax25 packet as packed bytes ON FAILURE: 0
def ax25encode(data, msgType: Literal["wod", "science"]):

    destAddr = b'\x88\x9E\x86\x96\x8A\xA4\xF6'      # 7 bytes that represent: 'D O C K E R 0b111SSID0' where SSID = 11 because that sat is a spacecraft
    if msgType == "science":
        sourAddr = b'\x8E\xA4\x9E\xAA\x9C\x88\xFF'  # 7 bytes that represent: 'G R O U N D 0b111SSID1' where SSID = 0b1111 for science data
    else:
        sourAddr = b'\x8E\xA4\x9E\xAA\x9C\x88\xFD'  # 7 bytes that represent: 'G R O U N D 0b111SSID1' where SSID = 0b1110 for WOD data
    control = b'\x03'
    protocol = b'\xf0'
    information = data
    fcs = b'\x11\x11'

    if type(data) is bytes:
        if len(data) <= 256:
            preStuffed = destAddr + sourAddr + control + protocol + information + fcs
            ax25 = stuffPacket(preStuffed)
            return ax25
        else:
            print("DATA WAS TOO LONG FOR AX25!")
        return 0
    else:
        print("DATA WAS NOT OF BYTES TYPE FOR AX25!")
        return 0


# Function breaks down an ax25 packet (byte type) into constituent parts
# returns ax25 object with attributes containing the packets important information
def ax25decode(packet):
    if (len(packet) < 20):
        print("ERROR: ax25decode, packet not in ax25 UI format")
        return 0

    packet = unstuffPacket(packet)
    decodedPacket = ax25info()

    destAddr = ""
    for i in packet[1:7]:
        shiftByte = chr(i >> 1)
        destAddr = destAddr + shiftByte
    decodedPacket.destAddr = destAddr

    decodedPacket.destSSID = (packet[7] >> 1) & 0b1111

    sourAddr = ""
    for i in packet[8:14]:
        shiftByte = chr(i >> 1)
        sourAddr = sourAddr + shiftByte
    decodedPacket.sourAddr = sourAddr

    decodedPacket.sourSSID = (packet[14] >> 1) & 0b1111

    decodedPacket.data = packet[17:-3]

    decodedPacket.fcs = packet[-3:-1]

    return decodedPacket


# Function takes in an ax25 packet (WITHOUT FLAGS) before transmission and byte-stuffs the
# accidental flags (0x7E) with an escape character (0x7D) then adds the actual flags
# returns a stuffed packet
def stuffPacket(packet):
    stuffedPacket = packet.replace(ESCAPE, ESCAPE + ESCAPE)
    stuffedPacket = stuffedPacket.replace(FLAG, ESCAPE + FLAG)
    stuffedPacket = FLAG + stuffedPacket + FLAG
    return stuffedPacket


# Function takes in a byte-stuffed ax25 packet and removes the stuffing but retains the flags
# returns the unstuffed packet w/ flags
def unstuffPacket(packet):
    unStuffedPacket = packet.replace(ESCAPE + FLAG, FLAG)
    unStuffedPacket = unStuffedPacket.replace(ESCAPE + ESCAPE, ESCAPE)
    return unStuffedPacket