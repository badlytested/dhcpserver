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

#Initiate an instance of a DHCP server at the given address. This address should match the static IP of the NIC you are
#distributing addresses on.
my_server = DHCP.DHCP_Server('192.168.6.1')

#This class is a requirement of the socketserver object. Its method 'handle' defines what happens when the server receives a request.
class DHCP_req_handle(socketserver.BaseRequestHandler):

    def handle(self):

        #create the message object. Since the server is listening on port 67, it assumes that any request received is a DHCP request.
        #It is unknown what will happen if this server receives a BOOTP request. Probably nothing as the DHCP options field factors
        #heavily in the behavior of the server. self.request is a tuple of the recieved data and the client socket.
        request = DHCP.Message(self.request[0])

        #When a request is recieved, show the DHCP message type, the MAC its from, and the transaction ID. For info/debug purposes.
        print('DHCP ', DHCP.get_key(DHCP.dhcp_message_types, request.options['dhcp message type']), ' from: ', request.chaddr[:6].hex(), ', xid: ', request.xid.hex())

        #Check that the code knows how to handle the message properly, then assemble and send the response to the broadcast address.
        if request.options['dhcp message type'] == b'\x01' or request.options['dhcp message type'] == b'\03':

            #creates a new server response object and calls the assemble method to pack the attributes into a byte string. Unknown if the response needs to be
            #padded as it is with the ljust. That was added while trying to get the responses right but not sure if it makes a difference.
            responsedata = DHCP.Server_Response(request, my_server).assemble_response().ljust(300, b'\x00')

            #self.request[1] is a socket object that was created when the request was recieved. This modifies it to use the broadcast address and sends the
            #response to the DHCP client port. 
            response = self.request[1]
            response.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            response.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            response.sendto(responsedata, ('<broadcast>', 68))

            #TODO: A console notification that a response was sent, the type, etc.
            print('sent response') 


if __name__ == '__main__':
    with socketserver.UDPServer(('', 67), DHCP_req_handle) as server:
        print('server started')
        server.serve_forever()


#TODO: See if I can delete the ljust call on the responsedata.