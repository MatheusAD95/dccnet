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
	    header32 = con.recv(4)
	    Header1 =  hex(struct.unpack('!I',header32)[0])
	    header2 = con.recv(4)
	    Header2 =  hex(struct.unpack('!I',header2)[0])
	    check = con.recv(4)
	    Check  = hex(struct.unpack('!I',check)[0])
	    length = con.recv(4)
	    Length =  hex(struct.unpack('!I',length)[0])
	    iD  = con.recv(4)
	    ID = hex(struct.unpack('!I',iD)[0])
	    print ID
	    data = con.recv(int(struct.unpack('!I',length)[0]))
	    Data =  hex(struct.unpack('!I',data)[0])
	    print Data
	    preframe = Header1[2:] +Header2[2:]+'0000'+Length[2:].zfill(4)+ID[2:].zfill(4)+Data[2:]
	    print preframe
	    print Check[2:]
	    print errorChk.checksum(preframe)
	    if Check[2:] == errorChk.checksum(preframe):
			break
	con.close()
