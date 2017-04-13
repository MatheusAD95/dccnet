import struct
import socket
import sys
import 
#toDo add checksum to frame
#check if it is right to do data/2
#change HOST and PORT to spec 
#figure if the read 1 2 3 4 is always equal 01 02 03 04, we read 1 2 3 4 from file or 01 02 03 04, how to diferentiate 12 from 1 2 
HOST = '127.0.0.1'
PORT = 51515
header = 'dcc023c2dcc023c2'
syncNum = '0'.zfill(4)
f = open(sys.argv[1],'r')
data = f.read()
length =str(len(data)/2)
if int(length) % 2 != 0:
  	data = data.ljust(2*int(length)+2,'0')
print data
length = length.zfill(4)
preframe =  header+'0000'+length+syncNum+data
check = errorChk.checksum(preframe)
frame = header+check+length+syncNum+data
print frame
frame = header+length+syncNum+data #add checksum
dest = (HOST,PORT)
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



