import struct
import socket
import sys
import checksum as errorChk
if sys.argv[1] == "-s":
  HOST = ''              # Endereco IP do Servidor
	PORT = int(sys.argv[2])
	syncNum = 0    # Porta que o Servidor esta
	print "this is the server"
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	orig = (HOST, PORT)
	print HOST
	tcp.bind(orig)
	tcp.listen(1)
	while True:
	  con, cliente = tcp.accept()
	  print 'Conectado por', cliente
	  con.send(str(syncNum))
	  while True:
	    header1 = con.recv(4)
	    print hex(struct.unpack('!I',header1)[0])
	    header2 = con.recv(4)
	    print hex(struct.unpack('!I',header2)[0])
	    check = con.recv(4)
	    Check hex(struct.unpack('!I',check)[0])
	    length = con.recv(4)
	    Length =  hex(struct.unpack('!I',length)[0])
	    iD  = con.recv(4)
	    ID = hex(struct.unpack('!I',ID)[0])
	    data = con.recv(int(struct.unpack('!I',length)[0])*2)
	    Data =  hex(struct.unpack('!I',data)[0])
	    if check == errorChk.checksum(header1)[2:] +hex(header2)[2:]+'0000'+str(length).zfill(4)+str(sync).zfill(4)+str(Data)):
	      con.send(str(syncNum))
	      break
	con.close()
