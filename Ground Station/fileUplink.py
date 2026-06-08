from ax25 import *
import csv
import struct
import socket

EXPERIMENT_SETTINGS_PATH = "./Uplink/experiment_settings.csv"
MAX_DATA_PER_PACKET = 180
RESULT_TIMESTEPS = 150

UPLINK_FILEID = 7



def load_settings(csv_path: str) -> bytes:
    """
    Read experiment_settings.csv and pack into the binary schema that
    ObcMessageHandler::deserialise() parses, in this exact field order:

      float frame_rate
      float threshold
      float exposure
      float positions[RESULT_TIMESTEPS][3]   (x, y, z)
      float attitudes[RESULT_TIMESTEPS][3]   (roll, pitch, yaw, in degrees)
      float sat_attitude[3]                  (in degrees)

    All floats are little-endian.
    """
    with open(csv_path, newline='') as f:
        rows = list(csv.reader(f))

    # Rows 0-2: one scalar per row
    frame_rate = float(rows[0][0])
    threshold  = float(rows[1][0])
    exposure   = float(rows[2][0])

    # Rows 3 to 3+RESULT_TIMESTEPS-1: platform positions
    positions = []
    for row in rows[3 : 3 + RESULT_TIMESTEPS]:
        positions.append([float(v) for v in row])

    # Rows 3+RESULT_TIMESTEPS to 3+2*RESULT_TIMESTEPS-1: platform attitudes (degrees)
    attitudes = []
    for row in rows[3 + RESULT_TIMESTEPS : 3 + 2 * RESULT_TIMESTEPS]:
        attitudes.append([float(v) for v in row])

    # Final row: satellite attitude (degrees)
    sat_attitude = [float(v) for v in rows[3 + 2 * RESULT_TIMESTEPS]]

    # Pack in schema order (little-endian floats)
    stream  = struct.pack('<f', frame_rate)
    stream += struct.pack('<f', threshold)
    stream += struct.pack('<f', exposure)
    for pos in positions:
        stream += struct.pack('<3f', *pos)
    for att in attitudes:
        stream += struct.pack('<3f', *att)
    stream += struct.pack('<3f', *sat_attitude)

    print(f"Packed {len(stream)} bytes from '{csv_path}'")
    return stream


def make_packets(data: bytes) -> list:
    """Split binary data into packet payloads, each prefixed with a 2-byte little-endian index."""
    packets = []
    for i in range(0, len(data), MAX_DATA_PER_PACKET):
        index   = struct.pack('<H', len(packets))
        payload = data[i : i + MAX_DATA_PER_PACKET]
        packets.append(index + payload)
    return packets


def send_header(packets: bytes, sock: socket):
    try:
        # Generate file information
        fileId = UPLINK_FILEID
        chunk_size = len(packets[0])
        num_chunks = len(packets)

        payload = struct.pack('<BII', fileId, chunk_size, num_chunks)
        encodedPacket = ax25encode(payload, msgType='science')
        
        # sendall() will raise an exception if the client disconnected
        sock.sendall(encodedPacket)
        print("File info sent successfully.")
        return True
        
    except (BrokenPipeError, ConnectionResetError, socket.error) as e:
        print(f"Client disconnected or connection lost: {e}")
        return False
    

def send_packets(packets: bytes, sock: socket):
    for i in range(len(packets)):
        try:
            # sendall() will raise an exception if the client disconnected
            encodedPacket = ax25encode(packets[i], msgType='science')
            sock.sendall(encodedPacket)
            print("Packet sent successfully.")
            
        except (BrokenPipeError, ConnectionResetError, socket.error) as e:
            print(f"Client disconnected or connection lost: {e}")
            return False
        
    return True