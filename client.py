import struct
import socket
import sys
import checksum as errorChk
if sys.argv[1] == "-c":
    (HOST, PORT) = sys.argv[2].split(":")
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((HOST, PORT))
    tcp.settimeout(5)
    sync = 0x0
    header = 0xdcc023c2;
    f = open(sys.argv[3],'r')
    data = f.read()
    length =len(data)
    print data
    preframe =  hex(header)[2:] +hex(header)[2:]+'0000'+str(length/2).zfill(4)+str(sync).zfill(4)+data
    print preframe
    check = errorChk.checksum(preframe)
    tcp.send(struct.pack("!I",header))
    tcp.send(struct.pack("!I",header))
    tcp.send(struct.pack("!I", int(check,16)))
    tcp.send(struct.pack("!I",length/2))
    tcp.send(struct.pack("!I",sync))
    tcp.send(struct.pack("!I",int(data,16)))
    try:
    	ack = tcp.recv(1)
    except socket.timeout:
    	tcp.send(frame)	
    print ack
    tcp.close();
