import sys

types_s = b"""
namespace NetMsgType {
const char *VERSION="version";
const char *VERACK="verack";
const char *ADDR="addr";
const char *ADDRV2="addrv2";
const char *SENDADDRV2="sendaddrv2";
const char *INV="inv";
const char *GETDATA="getdata";
const char *MERKLEBLOCK="merkleblock";
const char *GETBLOCKS="getblocks";
const char *GETHEADERS="getheaders";
const char *TX="tx";
const char *HEADERS="headers";
const char *BLOCK="block";
const char *GETADDR="getaddr";
const char *MEMPOOL="mempool";
const char *PING="ping";
const char *PONG="pong";
const char *NOTFOUND="notfound";
const char *FILTERLOAD="filterload";
const char *FILTERADD="filteradd";
const char *FILTERCLEAR="filterclear";
const char *SENDHEADERS="sendheaders";
const char *FEEFILTER="feefilter";
const char *SENDCMPCT="sendcmpct";
const char *CMPCTBLOCK="cmpctblock";
const char *GETBLOCKTXN="getblocktxn";
const char *BLOCKTXN="blocktxn";
const char *GETCFILTERS="getcfilters";
const char *CFILTER="cfilter";
const char *GETCFHEADERS="getcfheaders";
const char *CFHEADERS="cfheaders";
const char *GETCFCHECKPT="getcfcheckpt";
const char *CFCHECKPT="cfcheckpt";
const char *WTXIDRELAY="wtxidrelay";
} // namespace NetMsgType
"""

types_s1 = types_s.split(b"const char")
types = []
for t in types_s1:
    if b'"' in t:
        types.append(t.split(b'"')[1])

#For now just use an "everything goes" swarm
new_data = b""
for i in range(len(types)):
    new_data.append(b"\xff")

with open(sys.argv[1], "rb") as original:
    data = original.read()
print (type(data))

pos = 0
while (pos < len(data)):
    t_pos = data.find(b"\x00", pos)
    if t_pos != -1:
        t = data[pos:t_pos]
        if t in types:
            print("TYPE:", t, "@", pos)
            which_t = types.index(t)
            new_data += bytes(chr(which_t), encoding="utf-8")
            pos = t_pos + 1
            
    else:
       new_data += data[pos]   
    pos += 1

with (open(sys.argv[2], "wb") as new:
      new.write(new_data)
