import socket
from enum import Enum
from ax25 import *

SAT_IP = "192.168.1.1"
SAT_PORT = 4210

# Task requests for the satelliteto carry out. This is the data in the first packet sent to the satellite.
# The satellite knows what data to send back or function to perform based on this first packet
WOD_DOWNLINK = 1
SCI_DOWNLINK = 2
CLEAR_WOD = 3


class satClient:

    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # TCP Setup

    # Connect client to satellite server.
    # Returns: 1 if successful, 0 if connection failed
    def connectToSat(self):
        try:
            self.sock.connect((SAT_IP, SAT_PORT))
            print(f"Connected to ESP32 at {SAT_IP}")
            return 1
        except socket.error:
            print("Failed to connect to Satellite Server")
            return 0

    # Below funciton works with Docker_TCP_Test running on ESP32. Use it to verify hardware
    # Function send hello world, and ESP32 sends a acknowlegment response back
    def testPing(self):
        msg = "Hello, world\n"
        self.sock.sendall(msg.encode())
        data = self.sock.recv(1024).decode('utf-8')          # blocking
        print(f"Received from ESP32: {data}")

    def wodDownlink(self):
        #request = WOD_DOWNLINK.to_bytes(3, byteorder='big')
        request = "Hello, world"
        request = request.encode()
        msg = ax25encode(request, msgType='wod')
        self.sock.sendall(msg)

        packet = []
        while True:
            rxData = self.sock.recv(100)

            if not rxData:
                break

            packet.append(rxData)

        packet = b''.join(packet)

        print("RAW DATA:", packet.hex(' '))
        decodedPacket = ax25decode(packet)
        if(decodedPacket):
            print("DESTINATION ADDRESS:", decodedPacket.destAddr)
            print("DESTINATION SSID:", decodedPacket.destSSID)
            print("SOURCE ADDRESS:", decodedPacket.sourAddr)
            print("SOURCE SSID:", decodedPacket.sourSSID)
            print("INFORMATION FIELD:", decodedPacket.data.decode('utf-8'))
            print("FCS:", decodedPacket.fcs.hex(' '))

    def closeClient(self):
        self.sock.close()
        print("satClient socket closed\n")