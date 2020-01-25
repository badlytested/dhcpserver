'''DHCP Server Port: 67'''
#DHCP Client Port: 68

###DHCP Process - IDEAL###
# DHCPDISCOVER - Client broadcast to locate available servers.
'''DHCPOFFER - Server responds with offer of config parameters'''
# DHCPREQUEST - Client responds accepting offered params, confirms previously allocated addr, or extends lease of addr.
'''DHCPACK - Server to client with config parameters, including committed network address.'''

###DHCP Other Messages###
'''DHCPNAK - Server informs client that its notion of network address is incorrect'''
# DHCPDECLINE - Client tells server network address is already in use.
# DHCPRELEASE - Client relinquishes network address and cancels remaining lease.
# DHCPINFORM - Client request for local config parameters, client has externally configured address.

'''my NICs:

Ethernet: 00-4E-01-9A-E5-93
Loopback: 02-00-4C-4F-4F-50
Wi-Fi: A0-51-0B-47-B2-83
'''


import socketserver
from socket import *
import DHCP

my_server = DHCP.DHCP_Server('192.168.6.1')



class DHCP_req_handle(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request

        #create the message object
        request = DHCP.Message(data[0])
        print(data[0])

        #receive the discovery message, create and send an offer. 
        if request.options['dhcp message type'] == '01':
            print('DHCP Discover Message from', request.chaddr[:12], 'xid: ', request.xid)
            responsedata = DHCP.Server_Response(request, my_server).assemble_response().ljust(300, b'\x00')
            response = self.request[1]

            response.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            response.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            response.sendto(responsedata, ('<broadcast>', 68))

        #receive the configuration request, commit config and acknowledge
        if request.options['dhcp message type'] == '03':
            print('DHCP Config Request Message from', request.chaddr[:12])
            responsedata = DHCP.Server_Response(request, my_server).assemble_response().ljust(300, b'\x00')
            response = self.request[1]

            response.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            response.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            response.sendto(responsedata, ('<broadcast>', 68))

if __name__ == '__main__':
    with socketserver.UDPServer(('', 67), DHCP_req_handle) as server:
        print('server started')
        server.serve_forever()


