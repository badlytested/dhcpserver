import socketserver
import socket

class Message:
    def __init__(self, data):
        self.messageType = data[0:2]
        self.hwType = data[2:4]
        self.hwLength = data[4:6]
        self.hops = data[6:8]
        self.xid = data[8:16]
        self.secs = data[16:20]
        self.flags = data[20:24]
        self.ciaddr = data[24:32]
        self.yiaddr = data[32:40]
        self.siaddr = data[40:48]
        self.giaddr = data[48:56]
        self.chaddr = data[56:88]
        self.sname = data[88:216]
        self.file = data[216:472]
        self.magic = data[472:480]

class myUDPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = self.request
        socket = self.request[1]

        print(data[0].hex())
        mess = Message(data[0].hex())
        print(mess.xid, mess.chaddr, mess.magic)


if __name__ == '__main__':
    HOST, PORT = '', 67
    with socketserver.UDPServer((HOST, PORT), myUDPHandler) as server:
        print('server started')
        server.serve_forever()

