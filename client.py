import socket
from struct import pack, unpack
from sys import argv
from checksum import checksum

#TODO divide data into (256 - 112) bits blocks?
def recv4B(con):
    data = con.recv(4)
    unpacked_data = unpack('!I', data)[0]
    return unpacked_data

def send_frame(con, ID, data, flag_end):
    header = 0xdcc023c2
    frame = hex(header)[2:] + hex(header)[2:]
    # placeholder for the checksum
    frame += '0000'
    endt = 0
    if flag_end == 1:
        endt = endt | 0x80
    # len computes the number of bytes, but we need the number of 16bits blocks
    length = len(data)/2
    frame += str(length).zfill(4)
    frame += str(ID).zfill(4)
    frame += data
    print hex(endt)
    cs = checksum(frame)
    con.send('a')
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    #con.send(pack("!I", cs))
    #con.send(pack("!I", length))
    #con.send(pack("!I", ID))
    #con.send(0x80)
    #TODO zfill data in a way that it always has an even length
    #con.send(data)
    return cs

def recv_ack_frame(con, ID, cs):
    sync1 = recv4B(con)
    sync2 = recv4B(con)
    while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
	sync1 = sync2
	sync2 = recv4B(con)
    ack_cs = recv4B(con)
    length = recv4B(con)
    ack_ID = recv4B(con)
    if cs == ack_cs and ack_ID == ID and length == 0:
	return True
    return False

if argv[1] == "-c":
    (HOST, PORT) = argv[2].split(":")
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, int(PORT)))
    tcp.settimeout(5)
    f = open(argv[3],'r')
    data = f.read()
    length = len(data)
    data_len = length/256
    ID = 0
    end_flag = 0
    ack = 0
    for i in range(0, data_len + 1):
        while ack == 0:
            if i == data_len:
                end_flag = 1
            a = i*256
            b = a + 256
            if i == data_len :
                b = length % 256
            cs = send_frame(tcp, ID, data[a:b],end_flag)
            try:
                if recv_ack_frame(tcp, ID, cs):
                    ack = 1
            except socket.timeout:
                ack = 0
        print "Send sucessfull"
    tcp.close();
