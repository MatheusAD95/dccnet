import socket
import struct
HOST = ''              # Endereco IP do Servidor
PORT = 51515
syncNum = 0      # Porta que o Servidor esta
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
  msg = con.recv(28)
  length = msg[21:24]
  ID = msg[25:28]
  if int(ID) == syncNum:
    con.send(str(syncNum))
    if syncNum == 0:
      syncNum =1;
    else:
      syncNum = 0
  else:
    con.recv(28)
    length = msg[21:24]
    ID = msg[25:28]
  data = con.recv(int(length)*2)
con.close()
