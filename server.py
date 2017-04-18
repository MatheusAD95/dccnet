import socket
import struct
import checksum as errorChk
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
  while True:
    msg = con.recv(28)
    length = msg[21:24]
    ID = msg[25:28]
    check = msg[16:20]
    if int(ID) == syncNum:
      if syncNum == 0:
        syncNum = 1
      else:
        syncNum = 0
    else:
      con.recv(28)
      length = msg[21:24]
      ID = msg[25:28]
    data = con.recv(int(length)*2)
    msg = msg+data
    if check == errorChk.checksum(msg):
      con.send(str(syncNum))
      break
con.close()
