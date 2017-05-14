import socket
from checksum import checksum
from sys import argv
from struct import pack, unpack

def recv4B(con):
    data = con.recv(4)
    unpacked_data = unpack('!I', data)[0]
    return unpacked_data

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

def unpack_data(data):
    udata = ""
    length = len(data)
    for byte in data:
        udata += hex(unpack("!B", byte)[0])[2:].zfill(2)
    return udata

def recv_frame(con):
    (sync1, sync2, rsync) = sync_packet(con)
    # receives data until it finds the double sync 0xdcc023c2
    while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
        (sync1, sync2, rsync) = concat1B(con, rsync)
    cs = recv4B(con)
    length = recv4B(con)
    ID = recv4B(con)
    flags = unpack("!B", con.recv(1))[0]
    data = con.recv(length, 8)
    frame = hex(sync1)[2:] + hex(sync2)[2:]
    frame += '0000'
    frame += hex(length)[2:].zfill(4)
    frame += str(ID).zfill(2)
    frame += hex(flags)[2:].zfill(2)
    udata = unpack_data(data)
    frame += udata
    return (frame, ID, cs, flags)

def send_ack_frame(con, ID, cs, flags):
    header = 0xdcc023c2
    length = 0
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!I", cs))
    con.send(pack("!I", length))
    con.send(pack("!I", ID))
    con.send(pack("!B", flags | 0x80))

def recv_ack_frame(con, ID, cs):
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

def send_frame(con, ID, flags, data):
    header = 0xdcc023c2
    frame = hex(header)[2:] + hex(header)[2:]
    # placeholder for the checksum
    frame += '0000'
    length = len(data)
    udata = unpack_data(data)
    frame += str(length).zfill(4)
    frame += str(ID).zfill(2)
    frame += hex(flags)[2:].zfill(2)
    frame += udata
    cs = checksum(frame)
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!I", cs))
    con.send(pack("!I", length))
    con.send(pack("!I", ID)) #TODO byte??
    con.send(pack("!B", flags))
    con.send(data)
    return cs


def client(HOST, PORT, FNAME):
    FRAME_LENGTH = (128 - 112)/8
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, PORT))
    tcp.settimeout(5)
    f = open(FNAME, 'r')
    data = f.read()
    length = len(data)
    nframes = length/FRAME_LENGTH
    ID = 1
    for i in range(nframes + 1):
        ack = 0
        ID = (ID + 1)%2
        while ack == 0:
            a = i*FRAME_LENGTH
            b = a + FRAME_LENGTH
            flags = 0x00
            if i == nframes: #last frame
                flags |= 0x40 
                b = a + length%FRAME_LENGTH
            cs = send_frame(tcp, ID, flags, data[a:b])
            try:
                if recv_ack_frame(tcp, ID, cs):
                    ack = 1
            except socket.timeout:
                ack = 0
    tcp.close()

def server(PORT):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', PORT))
    tcp.listen(1)
    ID = 1
    flag = 0;
    while True:
        con, cliente = tcp.accept()
        while True:
            (frame, frameID, cs, flags) = recv_frame(con)
            fcs = checksum(frame)
            if fcs == cs and frameID != ID:
                ID = (ID + 1)%2
                send_ack_frame(con, frameID, cs, flags)
                if flags & 0x40:
                    break
            elif fcs == cs and frameID != ID:
                send_ack_frame(con, frameID, cs, flags)
        con.close()
    tcp.close()

#----------------------------------- MAIN ------------------------------------#
if argv[1] == "-c":
    (HOST, PORT) = argv[2].split(":")
    client(HOST, int(PORT), argv[3])
elif argv[1] == "-s":
    server(int(argv[2]))
