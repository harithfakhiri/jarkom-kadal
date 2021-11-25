import socket
from utility import *
import sys
import threading
import queue
import base64

PORT = int(sys.argv[1])
PATH = sys.argv[2]
print(PORT, PATH)
SERVER = ''
ADDR = (SERVER, PORT)
N = 3

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDR)



def getFile(path):
    print("Reading file..")
    file = open(path, "rb")

    data = base64.b64encode(file.read())
    file.close()
    print("Reading success")
    print("splitting file..")
    D = []

    for i in range(0, len(data), MAX_DATA):
        if (i+MAX_DATA < len(data)):
            D.append(data[i:i+MAX_DATA])
        else:
            D.append(data[i:])
    print("splitting success")

    return D

def isAcked(sequences, addr, q):
    count = 0
    acks = []
    while count < len(sequences):
        conn, addr1 = server.recvfrom(MAX_PACKET)
        if (addr1 == addr):
            seq_num, ack_num, flag = getHeader(conn)
            if (flag == 0x8):
                acks.append(ack_num)
                count += 1
    acked = True
    for s in sequences:
        if s in acks:
            print(f"[Segment SEQ={s}] Acked")
        else:
            print(f"[Segment SEQ={s}] Not Acked")
            acked = False
    q.put(acked)

def send(data, addr):
    print(f"### Three-way handshake dengan {addr} ###")
    seq = 0
    server.sendto(pack(seq, 0, 0x40, None), addr)
    print("SYN-SENT")
    ack = False
    while not ack:
        conn, addr1 = server.recvfrom(MAX_PACKET)
        seq_num, ack_num, flag = getHeader(conn)
        if (addr1 == addr and flag == 0x48 and ack_num == seq+1):
            ack = True
            print("Acked, SYN-Received")
    seq = seq+1
    ack1 = seq_num + 1
    server.sendto(pack(seq, ack1, 0x8, None), addr);
    print("Ack sent")
    print("Connection Established")

    #kirim packets
    print("sending data...")

    length = len(data)
    print(f"{length} segments to send")
    sending = True
    while sending:
        sequences = []
        for i in range (N):
            if (seq+i <= length):
                sequences.append(seq+i)
        q = queue.Queue()
        thread = threading.Thread(target=isAcked, args=[sequences, addr,q])
        thread.start()
        for s in sequences:
            server.sendto(pack(s, s-1, 0, data[s-1]), addr)
            print(f"[Segment SEQ={s}] Sent")
        thread.join()
        if (q.get() == True):
            seq += len(sequences)
            if (seq > length):
                sending = False
        else:
            print("### Commencing Go Back-N Protocol")

    #closing connection
    seq = 100
    print("Closing connection...")
    server.sendto(pack(seq, 300, 0x88, None), addr)
    print("FIN,ACK sent")

    conn, addr1 = server.recvfrom(MAX_PACKET)
    seq_num, ack_num, flag = getHeader(conn)
    if (addr1 == addr and flag == 0x08 and ack_num == seq+1):
        print("Acked")

    conn, addr1 = server.recvfrom(MAX_PACKET)
    seq_num, ack_num, flag = getHeader(conn)
    if (addr1 == addr and flag == 0x88 and ack_num == seq+1):
        print("FIN, ACK received")
    
    server.sendto(pack(seq+1, seq_num+1, 0x8, None), addr)
    print("ACK sent")
    print("Connection closed")



def start():
    clients = []
    listen = True
    while listen:
        conn, addr = server.recvfrom(MAX_PACKET)
        clients.append((conn,addr))
        print(f"Client found ({addr})")
        more = input("listen more? (y/n)")
        if (more == "n"):
            listen = False

    for (conn, addr) in clients:
        send(getFile(PATH), addr)

print(f"Server starting at port {PORT} ...")
start()

