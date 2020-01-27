from struct import *

#Takes a typical IP address string and converts into in a byte object with length of 4.
def pack_ip(ipstr):
    import struct
    iparr = [int(each) for each in ipstr.split('.')]
    return struct.pack('BBBB', iparr[0], iparr[1], iparr[2], iparr[3])

#return a dictionary key for a given value.
def get_key(dictionary, val):
    for key in dictionary:
        if val == dictionary[key]:
            return key

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


dhcp_message_types = {
        'DISCOVER': b'\x01',
        'OFFER': b'\x02',
        'REQUEST': b'\x03',
        'DECLINE': b'\x04',
        'ACK': b'\x05',
        'NAK': b'\x06',
        'RELEASE': b'\x07',
        'INFORM': b'\x08'
        }

#Message object to be created when a DHCP message is received.
#The first thing the DHCPServer script does when the server recieves a request is create a message and
#parse the information based on the DHCP specification. A lot of this is not particularly useful and this could
#be scaled way down, however it is spelled out here for clarity, future use, and to help reinforce the
#DHCP specification.
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
        self.options = self.parse_DHCP_options(data[240:])

    #Read through the variable length option field of a dhcp message and return a dictionary.
    #Data parameter 'x' should be the options field from a DHCP message.
    #The options format is 1 byte option code, 1 byte length, n bytes value.
    #Code 255 indicates the end of the options field.
    def parse_DHCP_options(self, x):
        res = {}
        i = 0

        while i < len(x):
            #read option code and length
            code = x[i:i + 1]
            if code == b'\xff':
                break #If the option code is 255, you are done reading options.

            length = x[i + 1]

            #read remainder of option field based on the length.
            val = x[i + 2:i + 2 + length]
            
            #search for code in DHCP option codes and if it exists, append it to the result dictionary.
            try:
                res[op_codes[ord(code)]] = val
            except KeyError:
                print('Unknown Option Code: ', code)

            #Start the next iteration of the loop where the next option code should be.
            i += 2 + length

        return res


#A class that contains all the information necessary to respond appropriately to DHCP client requests.
#Like the Message class, this class spells out a lot more than might actually be necessary, but this way
#helps to ensure that it conforms properly to the DHCP spec and will make it easier in the future to implement
#more advanced features. 
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
        #Define the DHCP options for the response. These are stored as byte objects here because they have different types, in order to make
        #it easier when packing them up into the payload.
        self.options = {
            'dhcp message type': self.dhcp_message_type(request),
            'dhcp server ip': self.siaddr,
            'lease time': pack('L', 3600),
            'subnet mask': pack_ip(server.subnet),
            'router option': self.siaddr,
            'domain name': bytes(server.domain, 'ascii'),
            'dns': pack_ip(server.dns)
        }

    #Clients are allowed to request IP addresses, for example if they are configured to default to a particular IP address,
    #or are rewewing a lease. This function determines what IP address to give them. This needs a lot of work as currently
    #this code does not check to see if an IP address is occupied or is even in the same subnet as the server.
    def your_addr(self, request, server):

        if 'requested ip' in request.options:
            return request.options['requested ip']

        else:
            return pack_ip(server.next_ip())

    #Determine what type of response to give based on client request. There is only the most basic of error handling built in, using 
    #DHCP NAK messages as a catch all response.
    def dhcp_message_type(self, request, server):

        if request.options['dhcp message type'] == dhcp_message_types['DISCOVER']:
            return dhcp_message_types['OFFER']

        elif request.options['dhcp message type'] == dhcp_message_types['REQUEST']:
            return dhcp_message_types['ACK']

        elif request.options['dhcp message type'] == dhcp_message_types['DECLINE']:
            print(request.chaddr, 'reported ', server.cur_addr, 'is already in use!')
            return dhcp_message_types['OFFER']

        elif request.options['dhcp message type'] == dhcp_message_types['RELEASE']:
            print(request.chaddr, 'released its IP.')
            return dhcp_message_types['NAK']

        elif request.options['dhcp message type'] == dhcp_message_types['INFORM']:
            print(request.chaddr, 'sent a DHCP Inform message. Its gonna do its own thing...')
            return dhcp_message_types['NAK']

        else:
            print(request.chaddr, 'sent a message that was not understood')
            return dhcp_message_types['NAK']

    #This function packs each option defined in the __init__ function into the format [CODE][LENGTH][VALUES] as a bytearray object.
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

        #end code that must be added at the end of the DHCP options.
        res += b'\xff'

        return res

#This class defines the attributes of the created subnet and implements a basic method to increment IPs within that subnet.
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
        print(x)
        x[3] = str(int(x[3]) + 1)
        self.cur_addr = '.'.join(x)
        return '.'.join(x)
