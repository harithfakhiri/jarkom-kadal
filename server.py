# import socket
# import time

# server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# # Thanks to @stevenreddie
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# # Enable broadcasting mode
# server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# # Set a timeout so the socket does not block
# # indefinitely when trying to receive data.
# server.settimeout(0.2)
# message = b"your very important message"
# while True:
#     server.sendto(message, ('<broadcast>', 37020))
#     print("message sent!")
#     time.sleep(1)

# import socket

# UDP_IP = "127.0.0.1"
# UDP_PORT = 5005
 
# sock = socket.socket(socket.AF_INET, # Internet
#                socket.SOCK_DGRAM) # UDP
# sock.bind((UDP_IP, UDP_PORT))
 
# while True:
#     data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#     print("received message: %s" %data)

import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

server.bind((socket.gethostname(), 37020))
message = bytes("your very important message", "utf-8")
while True:
    clientsocket, address = server.accept()
    print(f"Connection form {address} has been established")
    clientsocket.send(message)