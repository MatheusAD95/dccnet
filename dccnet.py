import socket
from checksum import checksum
from sys import argv
from struct import pack, unpack

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
    cs = unpack("!H", con.recv(2))[0]
    length = unpack("!H", con.recv(2))[0]
    ID = unpack("!B", con.recv(1))[0]
    flags = unpack("!B", con.recv(1))[0]
    data = con.recv(length, 8)
    frame = hex(sync1)[2:] + hex(sync2)[2:]
    frame += hex(cs)[2:].zfill(4)
    frame += hex(length)[2:].zfill(4)
    frame += str(ID).zfill(2)
    frame += hex(flags)[2:].zfill(2)
    udata = unpack_data(data)
    frame += udata
    return (frame, ID, cs, flags, data, length)

def send_ack_frame(con, ID, cs, flags):
    header = 0xdcc023c2
    length = 0
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!H", cs))
    con.send(pack("!H", length))
    con.send(pack("!B", ID))
    con.send(pack("!B", flags | 0x80))

def send_frame(con, ID, flags, data):
    header = 0xdcc023c2
    frame = hex(header)[2:] + hex(header)[2:]
    frame += '0000' # placeholder for the checksum
    length = len(data)
    udata = unpack_data(data)
    frame += str(length).zfill(4)
    frame += str(ID).zfill(2)
    frame += hex(flags)[2:].zfill(2)
    frame += udata
    cs = checksum(frame)
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!H", cs))
    con.send(pack("!H", length))
    con.send(pack("!B", ID))
    con.send(pack("!B", flags))
    con.send(data)
    return cs

def server(PORT, INPUT, OUTPUT):
    FRAME_LENGTH = 128
    MAX_DATA_LENGTH = (FRAME_LENGTH - 112)/8
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', PORT))
    tcp.listen(1)
    ID = 1
    IDI = 0
    all_data_sent = 0
    all_data_recv = 0
    outf = open(OUTPUT, "w")
    con, cliente = tcp.accept()
    con.settimeout(5)
    inf = open(INPUT, "r")
    idata = inf.read(MAX_DATA_LENGTH)
    next_idata = inf.read(MAX_DATA_LENGTH)
    try:
        while all_data_sent == 0 or all_data_recv == 0:
            flags = 0x00
            if (next_idata == ""):
                flags |= 0x40 
            if (idata != ""):
                lcs = send_frame(con, IDI, flags, idata)
            else:
                all_data_sent = 1
            
            try:
                (frame, frameID, cs, flags, data, length) = recv_frame(con)
            except:
                lcs = send_frame(con, IDI, flags, idata)
            # ACK FRAME
            if cs == lcs and frameID == IDI and length == 0 and flags & 0x80:
                idata = next_idata
                next_idata = inf.read(MAX_DATA_LENGTH)
                IDI = (IDI + 1)%2
            # DATA FRAME
            else:
                fcs = checksum(frame) # error check (fcs should be equal to cs)
                if fcs == cs and frameID != ID:
                    outf.write(data)
                    ID = (ID + 1)%2
                    send_ack_frame(con, frameID, cs, flags)
                    if flags & 0x40:
                        all_data_recv = 1
                        outf.close()
                elif fcs == cs and frameID == ID:
                    send_ack_frame(con, frameID, cs, flags)
        inf.close()
        con.close()
        tcp.close()
    except: # if the client received the last frame it will send the ack
            # and then close the connection. The server may not receive this
            # ack, but all frames have been correctly sent
        inf.close()
        con.close()
        tcp.close()

def client(HOST, PORT, INPUT, OUTPUT):
    FRAME_LENGTH = 128
    MAX_DATA_LENGTH = (FRAME_LENGTH - 112)/8
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect((HOST, PORT))
    con.settimeout(5)
    ID = 1
    IDI = 0
    flag = 0;
    all_data_sent = 0
    all_data_recv = 0
    outf = open(OUTPUT, "w")
    inf = open(INPUT, "r")
    idata = inf.read(MAX_DATA_LENGTH)
    next_idata = inf.read(MAX_DATA_LENGTH)
    try:
        while all_data_sent == 0 or all_data_recv == 0:
            flags = 0x00
            if (next_idata == ""):
                flags |= 0x40 
            if (idata != ""):
                lcs = send_frame(con, IDI, flags, idata)
            else:
                all_data_sent = 1
            try:
                (frame, frameID, cs, flags, data, length) = recv_frame(con)
            except socket.timeout:
                lcs = send_frame(con, IDI, flags, idata)
            # ACK FRAME
            if cs == lcs and frameID == IDI and length == 0 and flags & 0x80:
                idata = next_idata
                next_idata = inf.read(MAX_DATA_LENGTH)
                IDI = (IDI + 1)%2
            # DATA FRAME
            else:
                fcs = checksum(frame) # error check
                if fcs == cs and frameID != ID:
                    outf.write(data)
                    ID = (ID + 1)%2
                    flags = 0x00
                    send_ack_frame(con, frameID, cs, flags)
                    if flags & 0x40:
                        all_data_recv = 1
                        outf.close()
                elif fcs == cs and frameID != ID:
                    send_ack_frame(con, frameID, cs, flags)
        inf.close()
        con.close()
    except: # if the server receives the last frame, sends ack but the
            # client doesnt recv the last ack the server will end up closing
            # the connection, but all data has been sent
        inf.close()
        con.close()


#----------------------------------- MAIN ------------------------------------#
if argv[1] == "-c":
    (HOST, PORT) = argv[2].split(":")
    client(HOST, int(PORT), argv[3], argv[4])
elif argv[1] == "-s":
    server(int(argv[2]), argv[3], argv[4])
