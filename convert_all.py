import os
import sys
import glob

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

print(len(types))
        
conversions = []
index = 0
for t in types:
    conversions.append((t + b"\x00", bytes(chr(index), encoding="utf-8")))
    index += 1
        
converted = 0
todo = len(glob.glob(sys.argv[1]))
        
for f in glob.glob(sys.argv[1]):
    converted += 1
    
    if os.path.exists("converted" + os.path.basename(f)):
        print("already converted", f)
        continue
    
    #For now just use an "everything goes" swarm
    new_data = b""
    for i in range(len(types)):
        new_data += b"\xff"

    with open(f, "rb") as original:
        data = original.read()

    for (corig, cnew) in conversions:
        data = data.replace(corig, cnew)
    new_data += data
        
    print("converted", f, converted, "/", todo)
    sys.stdout.flush()
    with open("converted." + os.path.basename(f), "wb") as new:
          new.write(new_data)
