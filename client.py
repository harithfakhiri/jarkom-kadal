# import socket

# client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

# # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).

# client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# # Enable broadcasting mode
# client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# client.bind(("", 37020))
# while True:
#     data, addr = client.recvfrom(1024)
#     print("received message: %s"%data)

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))