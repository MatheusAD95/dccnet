import socket
from struct import pack
from sys import argv
from checksum import checksum
#TODO divide data into (256 - 112) bits blocks?

def send_frame(con, ID, data):
    header = 0xdcc023c2
    frame = hex(header)[2:] + hex(header)[2:]
    # placeholder for the checksum
    frame += '0000'
    # len computes the number of bytes, but we need the number of 16bits blocks
    length = len(data)/2
    frame += str(length).zfill(4)
    # ID used to sync
    frame += str(ID).zfill(4)
    # data
    frame += data
    cs = checksum(frame)
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!I", cs))
    con.send(pack("!I", length))
    con.send(pack("!I", ID))
    #TODO zfill data in a way that it always has an even length
    con.send(data)

if argv[1] == "-c":
    (HOST, PORT) = argv[2].split(":")
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, int(PORT)))
    tcp.settimeout(5)
    f = open(argv[3],'r')
    data = f.read()
    length = len(data)
    ID = 0
    send_frame(tcp, ID, data)
    #try:
    #	ack = tcp.recv(1)
    #except socket.timeout:
    #	tcp.send(frame)	
    #print ack
    tcp.close();
