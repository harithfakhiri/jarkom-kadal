import sys
import socket
from utils import Utils, MAX_DATA_LENGTH
from time import sleep
import base64

addr = "0.0.0.0"
port = int(sys.argv[1])
clients = []
filepath = sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((addr, port))
sock.settimeout(2)
print(f"Server started at port  {port} ...")
print("Listening to broadcast address for clients.")

searching = True
count = 0
client = []
while searching:
	try:
		data, address = sock.recvfrom(1024)
	except socket.timeout as e:
		err = e.args[0]
		if err == 'timed out':
			sleep(2)
			print('no client')
			continue
		else:
			print(e)
			sys.exit(1)
	else:
		print(f"[!] Client ({address[0]}:{address[1]}) found")
		sock.sendto(b"Broadcast diterima", (address))
		client.append(address)
		continue_search = str(input("[?] Listen more ? (y/n) "))
		if (continue_search != "y"):
			searching = False
		count = count+1
clients = client

if (count == 0):
	print("No Client found")
else:
	print(count, "Clients found:")
	i = 0
	for i in range(len(client)):
		print(i+1, end="")
		print(".", client[i])
		i = i+1

def get_data(filepath):
	print("Reading file..")
	file = open(filepath, "rb")
	
	data = base64.b64encode(file.read())
	file.close()
	
	D = []
	for i in range(0, len(data), 32768):
		if (i+32768 < len(data)):
			D.append(data[i:i+32768])
		else:
			D.append(data[i:])
	print("splitting success")
	return D


def handshake(addr, port, clients, sock):

	for i in range(len(clients)):
		sequence_number = 1
		acknowledgement_number = 0
		packet = Utils(sequence_number, acknowledgement_number, 'SYN')
		sock.sendto(packet.convert_to_bytes(), clients[i])
		print(f"Sending {packet.flag} to {clients[i]}")
		recv_packet, address = sock.recvfrom(32780)
		recv_packet = Utils.convert_to_packet(recv_packet)
		print(f"Received {packet.flag} from {address}")
		if (recv_packet.flag == "SYN-ACK", recv_packet.acknowledge == (sequence_number+1)):
			sequence_number = recv_packet.acknowledge
			acknowledgement_number = recv_packet.sequence + 1
			packet = Utils(sequence_number, acknowledgement_number, 'ACK')
			sock.sendto(packet.convert_to_bytes(), clients[i])
			print(f"Sending {packet.flag} tp {clients[i]}")


def send_file(addr, port, clients, data_parts, sock):
	print("Commencing file transfer...")
	sb = 0
	N = len(data_parts)-1
	sm = N+1

	for i in range(len(clients)):
		sb = 0
		sm = N+1
		for j in range(sb, sm):
			packet = Utils(j, 0, "DATA", data=data_parts[j])
			print(f"[Segment SEQ={packet.sequence}] Sent")
			packet = packet.convert_to_bytes()
			sock.sendto(packet, clients[i])

		while True:
			data, address = sock.recvfrom(32780)
			recv_packet = Utils.convert_to_packet(data)
			if (recv_packet.acknowledge > sb and recv_packet.flag == "ACK"):
				print(f"[Segment SEQ={recv_packet.acknowledge-1}] Acked")
				if sm < len(data_parts) :
					sm = (sm - sb) + recv_packet.acknowledge
				else :
					sb = recv_packet.acknowledge
				if (recv_packet.acknowledge == len(data_parts)):
					packet = Utils(sb, 0, "FIN")
					packet = packet.convert_to_bytes()
					sock.sendto(packet, clients[i])
				else:
					packet = Utils(sm-1, 0, "DATA",
									data=data_parts[sm-1])
					print(f"[Segment SEQ={packet.sequence}] Sent")
					packet = packet.convert_to_bytes()
					sock.sendto(packet, clients[i])

			elif (recv_packet.flag == "FIN-ACK"):
				break

			else:
				for j in range(sb, sm):
					packet = Utils(sb, 0, "DATA", data=data_parts[j])
					print(f"[Segment SEQ={packet.sequence}] Sent")
					packet.create_checksum()
					packet = packet.convert_to_bytes()
					sock.sendto(packet, clients[i])
			sleep(2)
	sock.close()
	print("Server Connection Closed")

handshake(addr, port, clients, sock)
data_parts1 = get_data(filepath)
send_file(addr, port, clients, data_parts1, sock)