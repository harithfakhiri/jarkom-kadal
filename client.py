from os import close
import socket
import sys
from utils import Utils
from time import sleep
import base64

addr = socket.gethostname()
port = int(sys.argv[1])
path = sys.argv[2]
server_port = 3000
packet_dat = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((addr, port))
msg = b'Searching for Server'
print("broadcasting...")
sock.sendto(msg, ('255.255.255.255', 3000))
print("broadcasting succeeded")
response, addr = sock.recvfrom(32780)
print(response.decode("utf-8"), "from", addr)

def handshake(addr, port, sock):
	recv_packet, address = sock.recvfrom(32780)
	recv_packet_dat = Utils.convert_to_packet(recv_packet)
	print(f"Received {recv_packet_dat.flag} from {address}")
	if (recv_packet_dat.flag == "SYN"):
		seq_num = 1
		ack_num = recv_packet_dat.sequence + 1
		packet_dat = Utils(seq_num, ack_num, 'SYN-ACK')
		print(f"Sending {packet_dat.flag} to {address}")
		sock.sendto(packet_dat.toBytes(), addr)
	recv_packet, address = sock.recvfrom(32780)
	recv_packet_dat = Utils.convert_to_packet(recv_packet)
	print(f"Received {recv_packet_dat.flag} from {address}")

def recmsg(addr, port, filepath, packet_dat, sock):
	rn = 0
	f = open(filepath, 'wb+')
	while (True):
		recv_packet, addr = sock.recvfrom(32780)
		recv_packet_dat = Utils.convert_to_packet(recv_packet)
		if (recv_packet_dat.flag == "FIN"):
			packet_dat = Utils(0, rn, "FIN-ACK")
			packet_dat = packet_dat.toBytes()
			sock.sendto(packet_dat, addr)
			print(f'[Segment SEQ={recv_packet_dat.sequence}] Received, Ack sent')
			break
		else:
			if (recv_packet_dat.sequence == rn and recv_packet_dat.checksum == recv_packet_dat.Checkingsum()):
				packet_dat.append(recv_packet)
				f.write(base64.b64decode(recv_packet_dat.data))
				rn += 1
			packet_dat = Utils(0, rn, "ACK")
			packet_dat = packet_dat.toBytes()
			sock.sendto(packet_dat, addr)
			print(f'[Segment SEQ={recv_packet_dat.sequence}] Received, Ack sent')
	f.close()
	sock.close()
	print("Client Connection Closed")

handshake(addr, port, sock)
recmsg(addr, port, path, packet_dat, sock)