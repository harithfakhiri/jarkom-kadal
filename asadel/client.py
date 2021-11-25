from os import close
import socket
import sys
from packet import Packet, MAX_DATA_LENGTH
from time import sleep

TIMEOUT = 3


class Client():
    def __init__(self, address, port, server_address, server_port, filepath):
        self.address = address
        self.port = port
        self.server_address = server_address
        self.server_port = server_port
        self.packets = []
        self.filepath = filepath

    def search_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((self.address, self.port))
        print('this client ip and port is:', sock.getsockname())
        message = b'hello'
        print("sending to broadcast")
        sock.sendto(message, ('255.255.255.255', 3000))
        print("sending succeeded")
        response, addr = sock.recvfrom(32780)
        print(response.decode("utf-8"), "dari address:", addr)

    def three_way_handshake(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))
        recv_packet, addr = sock.recvfrom(32780)
        recv_packet = Packet.convert_to_packet(recv_packet)
        print(f"Received {recv_packet.flag} from {addr}")
        if (recv_packet.flag == "SYN"):
            sequence_number = 1
            acknowledgement_number = recv_packet.sequence + 1
            packet = Packet(sequence_number, acknowledgement_number, 'SYN-ACK')
            print(f"Sending {packet.flag} to {addr}")
            sock.sendto(packet.convert_to_bytes(), addr)
        recv_packet, addr = sock.recvfrom(32780)
        recv_packet = Packet.convert_to_packet(recv_packet)
        print(f"Received {recv_packet.flag} from {addr}")

    def receive_file(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))
        rn = 0
        f = open(self.filepath, 'ab')
        while (True):
            recv_packet, addr = sock.recvfrom(32780)
            recv_packet = Packet.convert_to_packet(recv_packet)
            if (recv_packet.flag == "FIN"):
                packet = Packet(0, rn, "FIN-ACK")
                packet = packet.convert_to_bytes()
                sock.sendto(packet, addr)
                print(
                    f'[Segment SEQ={recv_packet.sequence}] Received, Ack sent')
                break
            else:
                if (recv_packet.sequence == rn and recv_packet.checksum == recv_packet.create_checksum()):
                    self.packets.append(recv_packet)
                    f.write(recv_packet.data)
                    rn += 1

                packet = Packet(0, rn, "ACK")
                packet = packet.convert_to_bytes()
                sock.sendto(packet, addr)
                print(
                    f'[Segment SEQ={recv_packet.sequence}] Received, Ack sent')
        f.close()
        sock.close()
        print("Client Connection Closed")


port = int(sys.argv[1])
filepath = sys.argv[2]
print(port, filepath)
client = Client("127.0.0.1", port, "0.0.0.1", 3000, filepath=filepath)
client.search_server()
client.three_way_handshake()
client.receive_file()
