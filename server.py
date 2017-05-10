import struct
import socket
from sys import argv
from struct import pack, unpack
from checksum import checksum
#
# Receives 4 bytes from the connection
#
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
    print "LEN: "  + str(len(data))
    return (data, unpacked_data)

def concat1B(con, raw):
    nraw = raw[1:]
    nraw += con.recv(1)
    unpacked_data = unpack('!I', nraw)[0]
    return (unpacked_data, nraw)

def recv_frame(con):
    (rsync1, sync1) = recv4BR(con)
    while sync1 != 0xdcc023c2:
        #sync1 = concat1B(con, rsync1)
        print "LENRSYNC1: " + str(len(rsync1))
        (sync1, rsync1) = concat1B(con, rsync1)
    print hex(sync1)
    return ("0", "0", "0")
    #sync2 = recv4B(con)
    ## receives data until it finds the double sync 0xdcc023c2
    #while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
    #    sync1 = sync2
    #    sync2 = recv4B(con)
    #cs = recv4B(con)
    #length = recv4B(con)
    #ID = recv4B(con)
    #data = con.recv(4*length, 16)
    #frame = hex(sync1)[2:] + hex(sync2)[2:]
    #frame += '0000'
    #frame += str(length).zfill(4)
    #frame += str(ID).zfill(4)
    #frame += data
    #return (frame, ID, cs)

def send_ack_frame(con, ID, cs):
    header = 0xdcc023c2
    length = 0
    con.send(pack("!I", header))
    con.send(pack("!I", header))
    con.send(pack("!I", cs))
    con.send(pack("!I", length))
    con.send(pack("!I", ID))
    #TODO zfill data in a way that it always has an even length

if argv[1] == "-s":
    HOST = ''
    PORT = int(argv[2])
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((HOST, PORT))
    tcp.listen(1)
    ID = 1
    flag = 0;
    while True:
    	con, cliente = tcp.accept()
    	print 'Conectado por ', cliente
        while True:
    	    (frame, frameID, cs,flag) = recv_frame(con)
    	    print "Frame: " + frame
    	    if checksum(frame) == cs and frameID != ID:
    	        print "Data is correct. Preparing to send ack"
    	        send_ack_frame(con, frameID, cs)
    	        print "Ack sent"
                if flag == 1:
                    break
    con.close()
