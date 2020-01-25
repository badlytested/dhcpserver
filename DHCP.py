from struct import *


#Converts a hex value to a decimal number. ie '35' to '53'
def hex_dec(hex):
    dec = int(hex, 16)
    return dec

#Takes a typical IP address string and converts into in a byte object with length of 4.
def pack_ip(ipstr):
    import struct
    iparr = [int(each) for each in ipstr.split('.')]
    return struct.pack('BBBB', iparr[0], iparr[1], iparr[2], iparr[3])

#Takes a byte object length 4 and converts it into a readable IP string.
def unpack_ip(byteobj):
    import struct
    return '.'.join([str(x) for x in struct.unpack('BBBB', byteobj)])

#define options from RFC 2132. Not all will be implemented but some are included for future use/completeness.
#a code of 255 indicates an end of the options field.
op_codes = {
        1: 'subnet mask',
        2: 'time offset',
        3: 'router option',
        4: 'timer servers',
        5: 'name servers',
        6: 'dns',
        12: 'client host name',
        13: 'boot file size',
        15: 'domain name',
        19: 'ip fwd enable',
        21: 'policy filter',
        22: 'max datagram reassembly size',
        23: 'default time to live',
        28: 'broadcast address',
        29: 'mask discovery',
        30: 'mask supplier',
        31: 'router discovery',
        32: 'router solicitation',
        33: 'static route',
        36: 'eth encapsulate',
        42: 'NTP servers',
        43: 'vendor-specific info',
        50: 'requested ip',
        51: 'lease time',
        52: 'option overload',
        53: 'dhcp message type',
        54: 'dhcp server ip',
        55: 'param req list',
        56: 'message',
        57: 'max dhcp message size',
        58: 'renewal time',
        59: 'rebinding time',
        60: 'vendor class id',
        61: 'client identifier',
        66: 'tftp server name',
        67: 'boot file name',
    }

#return a dictionary key for a given value: NOT WORKING
def get_key(dictionary, val):
    for key in dictionary:
        if val == dictionary[key]:
            return key

dhcp_message_types = {
    'DISCOVER': b'\x01',
    'OFFER': b'\x02',
    'REQUEST': b'\x03',
    'DECLINE': b'\x04',
    'ACK': b'\x05',
    'NAK': b'\x06',
    'RELEASE': b'\x07',
    'INFORM': b'\x08'}

#read through the variable length option field of a dhcp message and return a dictionary
#data parameter should be the options field from a message.
def parse_DHCP_options(x):
    res = {}

    i = 0
    while i < len(x):

        #read first option code and length
        code = hex_dec(x[i:i + 2]) #35
        if code == 255:
            break

        length = hex_dec(x[i + 2:i + 4]) * 2 #1

        #read remainder of option field
        val = x[i + 4:i + 4 + length]
        
        #search for code in opCodes
        try:
            res[op_codes[code]] = val
        except KeyError:
            print('Unknown Option Code: ', code)

        i += length + 4

    return res

#Message object to be created when a DHCP message is received.
class Message:

    #Parse all the fixed length fields in the message, plus the options at the end.
    def __init__(self, data):
        self.messageType = data[0]
        self.hwType = data[1]
        self.hwLength = data[2]
        self.hops = data[3]
        self.xid = data[4:8]
        self.secs = data[8:10]
        self.flags = data[10:12]
        self.ciaddr = data[12:16]
        self.yiaddr = data[16:20]
        self.siaddr = data[20:24]
        self.giaddr = data[24:28]
        self.chaddr = data[28:44]
        self.sname = data[44:108]
        self.file = data[108:236]
        self.magic = data[236:240]
        self.options = parse_DHCP_options(data[240:].hex())



class Server_Response:

    def __init__(self, request, server):
        self.messageType = 2
        self.hwType = 1
        self.hwLength = 6
        self.hops = 0
        self.xid = request.xid
        self.secs = 0
        self.flags = 0
        self.ciaddr = request.ciaddr
        self.yiaddr = self.your_addr(request, server)
        self.siaddr = pack_ip(server.server_addr)
        self.giaddr = pack('l', 0)
        self.chaddr = request.chaddr
        self.sname = bytes(64)
        self.file = bytes(128)
        self.magic = request.magic
        self.options = {
            'dhcp message type': self.dhcp_message_type(request), #bytes
            'dhcp server ip': self.siaddr, #bytes
            'lease time': pack('L', 3600), #bytes
            'subnet mask': pack_ip(server.subnet), #bytes
            'router option': self.siaddr, #bytes
            'domain name': bytes(server.domain, 'ascii'), #bytes
            'dns': pack_ip(server.dns) #bytes
        }

    def your_addr(self, request, server):
        if 'requested ip' in request.options:
            print(request.options['requested ip'])

            iparr = []
            for octet in range(0, 8, 2):
                iparr.append(str(hex_dec(request.options['requested ip'][octet:octet + 2])))

            return pack_ip('.'.join(iparr))
        elif request.yiaddr == bytes(4):
            print(request.yiaddr, bytes(4))
            return pack_ip(server.next_ip())
        else:
            return request.yiaddr

    def dhcp_message_type(self, request):
        if request.options['dhcp message type'] == dhcp_message_types['DISCOVER'].hex():
            return dhcp_message_types['OFFER']
        elif request.options['dhcp message type'] == dhcp_message_types['REQUEST'].hex():
            return dhcp_message_types['ACK']
        else:
            return 'failed'

    #convert an option key and value to its proper byte format: [CODE][LENGTH][VALUES]
    def pack_option(self, opt):
        #get the key from the option name
        code = pack('B', get_key(op_codes, opt))
        #get the length of the values
        length = pack('B', len(self.options[opt]))
        #the value of the option
        values = self.options[opt]
        #assembles the option back into a byte string after initializing an empty bytestring
        res = bytearray() + code + length + values

        return res

    #assemble the UDP payload for a DHCP server response
    def assemble_response(self):
        res = bytearray()

        res.append(self.messageType)
        res.append(self.hwType)
        res.append(self.hwLength)
        res.append(self.hops)

        for each in self.xid:
            res.append(each)

        res += self.secs.to_bytes(2, byteorder='big')
        res += self.flags.to_bytes(2, byteorder='big')

        res += self.ciaddr

        res += self.yiaddr
        res += self.siaddr
        res += self.giaddr
        res += self.chaddr
        res += self.sname
        res += self.file
        res += self.magic
        
        for x in self.options:
            res += self.pack_option(x)

        res += b'\xff'

        return res







#DHCP Server object that takes an address and provides 
class DHCP_Server:

    def __init__(self, addr):
        self.server_addr = addr
        self.cur_addr = addr
        self.subnet = '255.255.255.0'
        self.hostname = 'quackDHCP'
        self.domain = 'quack'
        self.dns = '8.8.8.8'

    #increments the cur_addr attribute to assign the next available IP in the list to a Server_Response object.
    def next_ip(self):
        x = self.cur_addr.split('.')
        x[3] = str(int(x[3]) + 1)
        self.cur_addr = '.'.join(x)
        return '.'.join(x)




'''
my_server = DHCP_Server('192.168.6.1')

my_server_response = Server_Response(Message('0' * 512), my_server)

print(my_server.cur_addr)

my_server.next_ip()

print(my_server.cur_addr)'''