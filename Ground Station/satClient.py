import socket
from ax25 import *
from fileUplink import *

SAT_IP = "192.168.1.1"
SAT_PORT = 4210

# Task requests for the satelliteto carry out. This is the data in the first packet sent to the satellite.
# The satellite knows what data to send back or function to perform based on this first packet
WOD_DOWNLINK = 0
SCI_DOWNLINK = 1
CLEAR_WOD = 2
SEND_PARAMS = 3
TEST_OVERRIDE = 4


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
    # Function send hello world, and ESP32 sends a acknowlegment response back (AX.25 Format)
    def testPing(self):
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


    def wodDownlink(self):
        # SEND REQUEST PACKET
        request = WOD_DOWNLINK.to_bytes(1, byteorder='big')
        msg = ax25encode(request, msgType='wod')
        self.sock.sendall(msg)

        # RECIEVE AND STORE RAW WOD PACKETS
        with open("rawData.txt", "wb") as f:
            while True:
                rxData = self.sock.recv(1024)
                if not rxData:
                    print("All data recieved from Satellite, begin processing")
                    break
                f.write(rxData)


    def sciDownlink(self):
        # SEND REQUEST PACKET
        request = SCI_DOWNLINK.to_bytes(1, byteorder='big')
        msg = ax25encode(request, msgType='science')
        self.sock.sendall(msg)

        # RECIEVE AND STORE RAW SCI PACKETS
        with open("rawData.txt", "wb") as f:
            while True:
                rxData = self.sock.recv(1024)
                if not rxData:
                    print("All data recieved from Satellite, begin processing")
                    break
                f.write(rxData)


    def sendParams(self):
        # SEND REQUEST PACKET
        print("Sending experiment uplink request")
        request = SEND_PARAMS.to_bytes(1, byteorder='big')
        msg = ax25encode(request, msgType='science')
        self.sock.sendall(msg)

        # open a file and serialise the data
        serialisedFile = load_settings(EXPERIMENT_SETTINGS_PATH)
        packetsToSend = make_packets(serialisedFile)

        # send the file info packet
        if not (send_header(packetsToSend, self.sock)):
            return False

        # loop and send the remaining packets
        if not (send_packets(packetsToSend, self.sock)):
            return False
        
    
    def testOverride(self, device:int):
        # SEND OVERRIDE REQUEST PACKET
        request = TEST_OVERRIDE.to_bytes(1, byteorder='big')
        msg = ax25encode(request, msgType='science')
        self.sock.sendall(msg)
        override = device.to_bytes(1, byteorder='big')
        msg = ax25encode(override, msgType='science')
        self.sock.sendall(msg)



    def closeClient(self):
        self.sock.close()
        print("satClient socket closed\n")