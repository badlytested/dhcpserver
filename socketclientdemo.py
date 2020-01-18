import socket
import sys

HOST, PORT = '255.255.255.255', 9999
data = 'this is a test'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(bytes(data + '\n'), (HOST, PORT))
received = str(sock.recv(1024))

print('sent:       {}'.format(data))
print('received:   {}'.format(received))