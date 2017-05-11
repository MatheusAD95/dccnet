#TODO: checksum should take flags into account
#sync1    sync2    cs       len     ID      Flag    data
#dcc023c2 dcc023c2 faef     0004    00      00      01020304
#[0,8)    [8,16)   [16,20)  [20,24) [24,26) [26,28) [28, ..)
# 4         4        2        2       1       1
def checksum(f):
    length = int(f[20:24], 16)
    if length%2:
        f += "00" #TODO 0x00 nao o caracter '0'
    length *= 2 #length has to be multiplied by 2 since each byte is being
                #represented as two characters
    s = 0
    for i in range(0, 25, 4):
        s = s + int(f[i:i + 4], 16)
    s = s - int(f[16:20], 16)
    for i in range(28, 28 + length, 4):
        print f[i:i+4]
        s = s + int(f[i:i + 4], 16)
        print "done"
    carry = (s & 0xFFFF0000) >> 16
    return ~(carry + (s & 0xFFFF)) & 0xFFFF
