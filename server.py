import sys
import socket
from utils import Utils
from time import sleep
import base64

addr = "0.0.0.0"
port = int(sys.argv[1])
clients = []
filepath = sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((addr, port))
sock.settimeout(10)
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
			sleep(5)
			print('no client')
			continue
		else:
			print(e)
			sys.exit(1)
	else:
		print(f"[!] Client ({address[0]}:{address[1]}) found")
		sock.sendto(b"Broadcast accepted", (address))
		client.append(address)
		listen = str(input("[?] Listen more ? (y/n) "))
		if (listen != "y"):
			searching = False
		count = count+1
clients = client

if (count != 0):
	print(count, "Clients found:")
	i = 0
	for i in range(len(client)):
		print(i+1, end="")
		print(".", client[i])
		i = i+1
else:
	print("No Client found")

def get_data(filepath):
	print("Reading file..")
	file = open(filepath, "rb")
	
	data = base64.b64encode(file.read())
	file.close()
	
	D = []
	for i in range(0, len(data), 32768):
		if (i+32768 >= len(data)):
			D.append(data[i:])
			
		else:
			D.append(data[i:i+32768])
	print("split succeeded")
	return D


def handshake(clients, sock):

	for i in range(len(clients)):
		seq_num = 1
		ack_num = 0
		packet_dat = Utils(seq_num, ack_num, 'SYN')
		sock.sendto(packet_dat.toBytes(), clients[i])
		print(f"Sending {packet_dat.flag} to {clients[i]}")
		recv_packet, address = sock.recvfrom(32780)
		recv_packet_dat = Utils.convert_to_packet(recv_packet)
		print(f"Received {packet_dat.flag} from {address}")
		if (recv_packet_dat.flag == "SYN-ACK", recv_packet_dat.acknowledge == (seq_num+1)):
			seq_num = recv_packet_dat.acknowledge
			ack_num = recv_packet_dat.sequence + 1
			packet_dat = Utils(seq_num, ack_num, 'ACK')
			sock.sendto(packet_dat.toBytes(), clients[i])
			print(f"Sending {packet_dat.flag} to {clients[i]}")


def send_file(clients, data_parts, sock):
	print("Commencing file transfer...")
	sb = 0
	N = len(data_parts)-1
	sm = N+1

	for i in range(len(clients)):
		sb = 0
		sm = N+1
		for j in range(sb, sm):
			packet_dat = Utils(j, 0, "DATA", data=data_parts[j])
			print(f"[Segment SEQ={packet_dat.sequence}] Sent")
			packet_dat = packet_dat.toBytes()
			sock.sendto(packet_dat, clients[i])

		while True:
			data, address = sock.recvfrom(32780)
			recv_packet_dat = Utils.convert_to_packet(data)
			if (recv_packet_dat.acknowledge > sb and recv_packet_dat.flag == "ACK"):
				print(f"[Segment SEQ={recv_packet_dat.acknowledge-1}] Acked")
				if sm < len(data_parts) :
					sm = (sm - sb) + recv_packet_dat.acknowledge
				else :
					sb = recv_packet_dat.acknowledge
				if (recv_packet_dat.acknowledge == len(data_parts)):
					packet_dat = Utils(sb, 0, "FIN")
					packet_dat = packet_dat.toBytes()
					sock.sendto(packet_dat, clients[i])
				else:
					packet_dat = Utils(sm-1, 0, "DATA",
									data=data_parts[sm-1])
					print(f"[Segment SEQ={packet_dat.sequence}] Sent")
					packet_dat = packet_dat.toBytes()
					sock.sendto(packet_dat, clients[i])

			elif (recv_packet_dat.flag == "FIN-ACK"):
				break

			else:
				for j in range(sb, sm):
					packet_dat = Utils(sb, 0, "DATA", data=data_parts[j])
					print(f"[Segment SEQ={packet_dat.sequence}] Sent")
					packet_dat.Checkingsum()
					packet_dat = packet_dat.toBytes()
					sock.sendto(packet_dat, clients[i])
	sock.close()
	print("Server Connection Closed")

handshake(clients, sock)
data_parts1 = get_data(filepath)
send_file(clients, data_parts1, sock)