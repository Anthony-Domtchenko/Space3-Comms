
import crcmod
# Define the X-25 CRC function
crc_func = crcmod.predefined.mkCrcFun('x-25')

# Example data (AX.25 frame content)
data = b'\x88\x9E\x86\x96\x8A\xA4\xF6\x8E\xA4\x9E\xAA\x9C\x88\xFD\x03\xf0\x00'
fcs = crc_func(data)
print(type(fcs))
print(hex(fcs))