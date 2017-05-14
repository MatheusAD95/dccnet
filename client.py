import socket
from struct import pack, unpack
from sys import argv
from checksum import checksum

def recv4B(con):
    data = con.recv(4)
    unpacked_data = unpack('!I', data)[0]
    return unpacked_data

def send_frame(con, ID, flags, data):
    header = 0xdcc023c2
    frame = hex(header)[2:] + hex(header)[2:]
    # placeholder for the checksum
    frame += '0000'
    length = len(data)
    udata = unpack_data(data)
    print "DATA: " + udata
    print "LENGTH: " + hex(length)[2:].zfill(4) 
    frame += str(length).zfill(4)
    frame += str(ID).zfill(2)
    print "ID: " + str(ID).zfill(2)
    frame += hex(flags)[2:].zfill(2)
    print "flags: " + hex(flags)[2:].zfill(2)
    frame += udata
    print "checksum frame : " + frame
    cs = checksum(frame)
    con.send('a') #TODO remove this (its here just to test if we can sync)
    con.send('b')
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!I", cs))
    con.send(pack("!I", length))
    con.send(pack("!I", ID)) #TODO byte??
    con.send(pack("!B", flags))
    #TODO data should be packed/unpacked?
    con.send(data)
    return cs

def recv4BR(con):
    data = ""
    data += con.recv(1)
    data += con.recv(1)
    data += con.recv(1)
    data += con.recv(1)
    unpacked_data = unpack('!I', data)[0]
    return (unpacked_data, data)

def concat1B(con, rsync):
    new_byte = con.recv(1)
    new_sync = rsync[1:] + new_byte
    sync1 = unpack('!I', new_sync[:4])[0]
    sync2 = unpack('!I', new_sync[4:])[0]
    return (sync1, sync2, new_sync)

def sync_packet(con):
    (usync1, psync1) = recv4BR(con)
    (usync2, psync2) = recv4BR(con)
    return (usync1, usync2, psync1 + psync2)

def recv_ack_frame(con, ID, cs):
    #sync1 = recv4B(con)
    #sync2 = recv4B(con)
    #while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
    #    sync1 = sync2
    #    sync2 = recv4B(con)
    (sync1, sync2, rsync) = sync_packet(con)
    # receives data until it finds the double sync 0xdcc023c2
    while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
        (sync1, sync2, rsync) = concat1B(con, rsync)
    ack_cs = recv4B(con)
    length = recv4B(con)
    ack_ID = recv4B(con)
    flags = unpack("!B", con.recv(1))[0]
    if cs == ack_cs and ack_ID == ID and length == 0 and flags & 0x80:
	return True
    return False

#takes the binary data and converts it to a string representation
#occupying double the ammount of space
def unpack_data(data):
    udata = ""
    length = len(data)
    for byte in data:
        udata += hex(unpack("!B", byte)[0])[2:].zfill(2)
    return udata

#FRAME_LENGTH = (1024 - 112)/8 #112 bits are used for the header
FRAME_LENGTH = (128 - 112)/8 #112 bits are used for the header
if argv[1] == "-c":
    (HOST, PORT) = argv[2].split(":")
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, int(PORT)))
    tcp.settimeout(5)
    f = open(argv[3],'r')
    data = f.read()
    length = len(data)
    proc_data = ""
    for i in range(length):
        #print byte
        proc_data += hex(unpack("!B", data[i])[0])[2:].zfill(2)
        #proc_data.insert(0, hex(unpack("!B", byte)[0])[2:].zfill(2))
    print "PROC DATA: " + proc_data
    #print proc_data
    #data = proc_data
    #
    #hex(unpack(data[0]))[2:]
    #
    #print "PROC DATA" + proc_data
    #data = proc_data
    #print "DATA POST PROC DATA" + data
    nframes = length/FRAME_LENGTH
    ID = 1
    for i in range(nframes + 1):
        print "Preparing frame " + str(i)
        ack = 0
        ID = (ID + 1)%2
        while ack == 0:
            a = i*FRAME_LENGTH
            b = a + FRAME_LENGTH
            print "Interval: " + str(a) + " : " + str(b)
            print "Data from this frame: " + unpack_data(data[a:b])
            flags = 0x00
            if i == nframes: #last frame
                flags |= 0x40 
                b = a + length%FRAME_LENGTH
            print "Interval confirmation: " + str(a) + " : " + str(b)
            cs = send_frame(tcp, ID, flags, data[a:b])
            try:
                if recv_ack_frame(tcp, ID, cs):
                    ack = 1
            except socket.timeout:
                ack = 0
    print "All frames were sent sucessfully"
    tcp.close()
