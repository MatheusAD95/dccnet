def checksum(f):
    length = int(f[20:24], 16)
    s = 0
    for i in range(0, 25, 4):
        s = s + int(f[i:i + 4], 16)
    s = s - int(f[16:20], 16)
    #TODO can you always divide the message into 16 bits blocks? length%2 == 0?
    for i in range(28, 28 + length + 1, 4):
        s = s + int(f[i:i + 4], 16)
    carry = (s & 0xFFFF0000) >> 16
    return hex(~(carry + (s & 0xFFFF)) & 0xFFFF) [2:]
print hex(checksum("dcc023c2dcc023c2faef0004000001020304"))
