import struct
import socket
import sys
from struct import unpack
from checksum import checksum
#
# Receives 4 bytes from the connection
#
def recv4B(con):
    data = con.recv(4)
    unpacked_data = unpack('!I', data)[0]
    return unpacked_data

if sys.argv[1] == "-s":
    HOST = ''
    PORT = int(sys.argv[2])
    syncNum = 0
    print "this is the server"
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    orig = (HOST, PORT)
    print HOST
    tcp.bind(orig)
    tcp.listen(1)
    ID = 1
    while True:
	con, cliente = tcp.accept()
	print 'Conectado por ', cliente
	sync1 = recv4B(con)
	sync2 = recv4B(con)
	# receives data until it finds the double sync 0xdcc023c2
	while sync1 != 0xdcc023c2 and sync2 != 0xdcc023c2:
	    sync1 = sync2
	    sync2 = recv4B(con)
	print "Synced"
	cs = recv4B(con)
	print "Checksum: " + hex(cs)
	length = recv4B(con)
	print "Length: " + str(length)
	ID = recv4B(con)
	print "ID: " + str(ID)
	data = con.recv(4*length, 16)
	print "Data: " + data
	frame = hex(sync1)[2:] + hex(sync2)[2:]
	frame += '0000'
	frame += str(length).zfill(4)
	frame += str(ID).zfill(4)
	frame += data
	if checksum(frame) == cs:
	    con.send()
	    print "Data is correct. Preparing to send ack"
    con.close()
