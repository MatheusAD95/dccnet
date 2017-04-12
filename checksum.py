#dcc0 23c2 dcc0 23c2 faef 0004 0000 0102 0304
#0    4    8    12   16   20   24   28   32
#  32     32     16       16       16   length*8
#| SYNC | SYNC | chksum | length | ID | DADOS |
def checksum(f):
    sync0 = int(f[0:4], 16)
    sync1 = int(f[4:8], 16)
    length = int(f[20:24], 16)
    frame_id = int(f[24:28], 16)
    s = 2*(sync0 + sync1) + length + frame_id
    #TODO can you always divide the message into 16 bits blocks?
    #length%2 == 0?
    for i in range(28, 28 + length + 1, 4):
        s = s + int(f[i:i + 4], 16)
    a = (s & 0xFFFF0000) >> 16
    b = (s & 0x0000FFFF)
    c = ~(a + b) & 0xFFFF
    #print format(c, '06x')
    print hex(c)
checksum("dcc023c2dcc023c2faef0004000001020304")
