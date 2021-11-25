import base64
import socket
import random
import sys
from utility import *

PORT = 5050
BROADCAST = ('255.255.255.255', PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

CLIENT_PORT = int(sys.argv[1])
PATH = sys.argv[2]

def broadcast(msg):
    client.sendto(msg, (BROADCAST))

#check error
def check(packet):
    checksum = getCheckSum(packet)
    sum = getsum(getData(packet))
    return int.from_bytes(checksum, "big") + int.from_bytes(sum, "big") == 0xffff

print("broadcasting...")
broadcast("Broadcast".encode("utf-8"))

syn = False
while not syn:
    conn, server_addr = client.recvfrom(MAX_PACKET)
    seq_num, ack_num, flag = getHeader(conn)
    if (flag == 0x40):
        print(f"### Three-way handshake dengan {server_addr} ###")
        syn = True
        print("SYN-Received")
seq = 300
ack = seq_num + 1
client.sendto(pack(seq, ack, 0x48, None), server_addr)
print("SYN-Sent, Ack sent")

acked = False
while not acked:
    conn, addr = client.recvfrom(MAX_PACKET)
    seq_num, ack_num, flag = getHeader(conn)
    if (addr == server_addr and ack_num == seq+1):
        acked = True
        print("Acked")
print("Connection Established")
#terima packets
print("receiving data...")
received = [seq_num]
data = "".encode()
closing = False
while not closing:
    conn, addr = client.recvfrom(MAX_PACKET)
    seq_num, ack_num, flag = getHeader(conn)

    if(flag == 0x88):
        closing = True
    elif (check(conn)):
        received.append(seq_num)
        data += getData(conn)
        client.sendto(pack(random.randint(0, 2**32-1), seq_num, 0x8, None), addr)
        print(f"[Segment SEQ={seq_num}] Received, Ack sent")
    else:
        client.sendto(pack(random.randint(0, 2**32-1), received[-1], 0x8, None), addr)
        print(f"[Segment SEQ={seq_num}] Segment damaged. Ack prev sequence number.")
        print("### Expecting Go Back-N Protocol commencing ###")

#Closing connection
print("Closing connection...")
print("FIN, ACK received")
client.sendto(pack(ack_num, seq_num+1, 0x8, None), server_addr)
print("ACK sent")
client.sendto(pack(ack_num, seq_num+1, 0x88, None), server_addr)
print("FIN, ACK sent")
conn, addr = client.recvfrom(MAX_PACKET)
seq_num, ack_num, flag = getHeader(conn)
print("Connection Closed")

#writing file
file = open(PATH, "wb")
file.write(base64.b64decode(data))
print("file succesfully written")