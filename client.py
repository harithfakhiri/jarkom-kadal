from os import close
import socket
import sys
from utils import Utils, MAX_DATA_LENGTH
from time import sleep

addr = socket.gethostname()
port = int(sys.argv[1])
path = sys.argv[2]
server_address = "0.0.0.1"
server_port = 3000
packet = []
status= "CLOSED"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((addr, port))
print(f'Client ({sock.getsockname()}) found')
msg = b'assalamualaikum!'
print("broadcasting")
sock.sendto(msg, ('255.255.255.255', 3000))
print("broadcasting succeeded")
response, addr = sock.recvfrom(32780)
print(response.decode("utf-8"), "dari address:", addr)

def handshake(addr, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((addr, port))
	recv_packet, addr = sock.recvfrom(32780)
	recv_packet = Utils.convert_to_packet(recv_packet)
	print(f"Received {recv_packet.flag} from {addr}")
	if (recv_packet.flag == "SYN"):
		sequence_number = 1
		acknowledgement_number = recv_packet.sequence + 1
		packet = Utils(sequence_number, acknowledgement_number, 'SYN-ACK')
		print(f"Sending {packet.flag} to {addr}")
		sock.sendto(packet.convert_to_bytes(), addr)
	recv_packet, addr = sock.recvfrom(32780)
	recv_packet = Utils.convert_to_packet(recv_packet)
	print(f"Received {recv_packet.flag} from {addr}")

def recmsg(addr, port, filepath, packet):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((addr, port))
	rn = 0
	f = open(filepath, 'ab')
	while (True):
		recv_packet, addr = sock.recvfrom(32780)
		recv_packet = Utils.convert_to_packet(recv_packet)
		if (recv_packet.flag == "FIN"):
			packet = Utils(0, rn, "FIN-ACK")
			packet = packet.convert_to_bytes()
			sock.sendto(packet, addr)
			print(f'[Segment SEQ={recv_packet.sequence}] Received, Ack sent')
			break
		else:
			if (recv_packet.sequence == rn and recv_packet.checksum == recv_packet.create_checksum()):
				packet.append(recv_packet)
				f.write(recv_packet.data)
				rn += 1
			packet = Utils(0, rn, "ACK")
			packet = packet.convert_to_bytes()
			sock.sendto(packet, addr)
			print(f'[Segment SEQ={recv_packet.sequence}] Received, Ack sent')
	f.close()
	sock.close()
	print("Client Connection Closed")

handshake(addr, port)
recmsg(addr, port, path, packet)