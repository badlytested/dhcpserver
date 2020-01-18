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

''' sample stream 
01
01
06
00
b2c4382d
0400
0000
00000000
00000000
00000000
00000000
02004c4f4f5000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
63825363 #Magic Cookie, start of options.
350101
3d070102004c4f4f500c0b47756c6673747265616d353c084d53465420352e30370e0103060f1f212b2c2e2f7779f9fcff0000000000000000
'''

import socketserver

#Converts a hex value to a decimal number. ie '35' to '53'
def hexToDec(hex):
    dec = int(hex, 16)
    return dec

#Message object to be created when a DHCP message is received.
class Message:

    #Parse all the fixed length fields in the message, plus the options at the end.
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
        self.options = data[480:]

    #parse the variable length options in a message.
    def parseOptions(self):

