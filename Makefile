PORT=51000
HOST=127.0.0.1
CLIENT_I="client.i"
CLIENT_O="client.o"
SERVER_I="server.i"
SERVER_O="server.o"
client:
	python client.py -c $(HOST):$(PORT) $(CLIENT_I) $(CLIENT_O)
server:
	python server.py -s $(PORT) $(SERVER_I) $(SERVER_O)

