from ax25 import *


WOD_DOWNLINK = 1
SCI_DOWNLINK = 2
CLEAR_WOD = 3

'''
msg = b'\x7E\x7D'
print(msg)
stuffed = stuffPacket(msg)
print(stuffed)
unstuffed = unstuffPacket(stuffed)
print(unstuffed)
'''



msg = 3
msgA = msg.to_bytes(4, byteorder='big')
msgB = b'\x7E\x7D'

ax25msg = ax25encode(msgA, msgType='wod')


print(ax25msg)
print(type(ax25msg))

decoded = ax25decode(ax25msg)
print(decoded.data)


vector = "123"
sliced = vector[1:-2]
print(sliced)