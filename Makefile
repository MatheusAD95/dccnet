PORT=51005
HOST=127.0.0.1
CLIENT_I=client.i
CLIENT_O=client.o
SERVER_I=server.i
SERVER_O=server.o

client:
	python client.py -c $(HOST):$(PORT) $(CLIENT_I) $(CLIENT_O)
server:
	python server.py -s $(PORT) $(SERVER_I) $(SERVER_O)

s2:
	python server.py -s $(PORT2) $(SERVER_I) $(SERVER_O)
c2:
	python client.py -c $(HOST):$(PORT2) $(CLIENT_I) $(CLIENT_O)
