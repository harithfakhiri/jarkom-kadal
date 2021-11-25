import sys
import socket
from packet import Packet, MAX_DATA_LENGTH
from time import sleep

TIMEOUT = 1
N = 2


class Server:
    def __init__(self, address, port, filepath):
        self.address = address
        self.port = port
        self.clients = []
        self.packets = []
        self.filepath = filepath
        self.data_parts = []

    def get_data(self):
        f = open(self.filepath, 'rb')
        data = f.read()
        f.close()
        for i in range(0, len(data), 32768):
            self.data_parts.append(data[i:i+32768])

    def search_clients(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((self.address, self.port))
        sock.settimeout(2)
        print("Server started at port:", self.port)
        print("Listening to broadcast address for clients")
        searching = True
        count = 0
        client = []
        while searching:
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    sleep(1)
                    print('Tidak ada client')
                    continue
                else:
                    print(e)
                    sys.exit(1)
            else:
                print(f"[!] Client ({addr[0]}:{addr[1]}) found")
                sock.sendto(b"Broadcast diterima", (addr))
                client.append(addr)
                continue_search = str(input("[?] Listen lagi?(y/n)"))
                if (continue_search != "y"):
                    searching = False
                count = count+1
        self.clients = client

        if (count == 0):
            print("No Client found:")
        elif (count == 1):
            print("One Client found:")
            i = 0
            for i in range(len(client)):
                print(i+1, end="")
                print(".", client[i])
                i = i+1
        else:
            print(count, "Clients found:")
            i = 0
            for i in range(len(client)):
                print(i+1, end="")
                print(".", client[i])
                i = i+1

    def three_way_handshake(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))

        for i in range(len(self.clients)):
            sequence_number = 1
            acknowledgement_number = 0
            packet = Packet(sequence_number, acknowledgement_number, 'SYN')
            sock.sendto(packet.convert_to_bytes(), self.clients[i])
            print(f"Sending {packet.flag} to {self.clients[i]}")
            recv_packet, addr = sock.recvfrom(32780)
            recv_packet = Packet.convert_to_packet(recv_packet)
            print(f"Received {packet.flag} from {addr}")
            if (recv_packet.flag == "SYN-ACK", recv_packet.acknowledge == (sequence_number+1)):
                sequence_number = recv_packet.acknowledge
                acknowledgement_number = recv_packet.sequence + 1
                packet = Packet(sequence_number, acknowledgement_number, 'ACK')
                sock.sendto(packet.convert_to_bytes(), self.clients[i])
                print(f"Sending {packet.flag} to {self.clients[i]}")

    def send_file(self):
        print("Commencing file transfer...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))
        sb = 0
        sm = N+1

        for i in range(len(self.clients)):
            sb = 0
            sm = N+1
            for j in range(sb, sm):
                packet = Packet(j, 0, "DATA", data=self.data_parts[j])
                print(f"[Segment SEQ={packet.sequence}] Sent")
                packet = packet.convert_to_bytes()
                sock.sendto(packet, self.clients[i])

            while True:
                data, addr = sock.recvfrom(32780)
                recv_packet = Packet.convert_to_packet(data)
                if (recv_packet.acknowledge > sb and recv_packet.flag == "ACK"):
                    print(f"[Segment SEQ={recv_packet.acknowledge-1}] Acked")
                    sm = (sm - sb) + recv_packet.acknowledge if sm < len(
                        self.data_parts) else len(self.data_parts)
                    sb = recv_packet.acknowledge
                    if (recv_packet.acknowledge == len(self.data_parts)):
                        packet = Packet(sb, 0, "FIN")
                        packet = packet.convert_to_bytes()
                        sock.sendto(packet, self.clients[i])
                    else:
                        packet = Packet(sm-1, 0, "DATA",
                                        data=self.data_parts[sm-1])
                        print(f"[Segment SEQ={packet.sequence}] Sent")
                        packet = packet.convert_to_bytes()
                        sock.sendto(packet, self.clients[i])

                elif (recv_packet.flag == "FIN-ACK"):
                    break

                else:
                    for j in range(sb, sm):
                        packet = Packet(sb, 0, "DATA", data=self.data_parts[j])
                        print(f"[Segment SEQ={packet.sequence}] Sent")
                        packet.create_checksum()
                        packet = packet.convert_to_bytes()
                        sock.sendto(packet, self.clients[i])
                sleep(2)
        sock.close()
        print("Server Connection Closed")


port = int(sys.argv[1])
filepath = sys.argv[2]
print(port, filepath)
server = Server("0.0.0.0", port, filepath)
server.search_clients()
server.three_way_handshake()
server.get_data()
print("data length", len(server.data_parts))
server.send_file()
