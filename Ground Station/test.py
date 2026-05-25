from fileManipulation import *

filename = 'test.csv'
with open('rawData.txt', "rb") as f_in, open(filename, 'w', newline='', encoding='utf-8') as f_out:
    # Split raw data into AX25 packets by flag delimeters
    content = f_in.read()
    delimiter = b'\x7E'
    escape = b'\x7d'
    #ax25Chunks = content.split(delimiter)
    ax25Chunks = extract_frames(content, delimiter, escape)
    print(type(ax25Chunks))
    print(len(ax25Chunks))
    for i in ax25Chunks:
        print(i.hex(' '))