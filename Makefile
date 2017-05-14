PORT=51003
HOST=127.0.0.1
CLIENT_I=client.i
CLIENT_O=client.o
SERVER_I=server.i
SERVER_O=server.o

client:
	#python client.py -c $(HOST):$(PORT) $(CLIENT_I) $(CLIENT_O)
	python dccnet.py -c $(HOST):$(PORT) $(CLIENT_I) $(CLIENT_O)
server:
	python dccnet.py -s $(PORT) $(SERVER_I) $(SERVER_O)
