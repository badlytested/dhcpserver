
#Converts a hex value to a decimal number. ie '35' to '53'
def hex_dec(hex):
    dec = int(hex, 16)
    return dec


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
    '01': 'DISCOVER',
    '02': 'OFFER',
    '03': 'REQUEST',
    '04': 'DECLINE',
    '05': 'ACK',
    '06': 'NAK',
    '07': 'RELEASE',
    '08': 'INFORM'
}

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
        self.options = parse_DHCP_options(data[480:])

class Server_Response:

    def __init__(self, request, server):
        self.messageType = '02'
        self.hwType = '02'
        self.hwLength = '06'
        self.hops = '00'
        self.xid = request.xid
        self.secs = '0000'
        self.flags = '0000'
        self.ciaddr = request.ciaddr
        self.yiaddr = server.next_ip()
        self.siaddr = server.server_addr
        self.giaddr = '00000000'
        self.chaddr = request.chaddr
        self.sname = server.hostname.ljust(128, '0')
        self.file = '0' * 256
        self.magic = request.magic
        self.options = {
            'dhcp message type': '02',
            'dhcp server ip': self.siaddr,
            'lease time': '4294967295',
            'subnet mask': '255.255.255.0',
            'router option': self.siaddr,
            'domain name': server.domain,
            'dns': '8.8.8.8'
        }
        self.compiled_response = b'0000'



#DHCP Server object that takes an address and provides 
class DHCP_Server:

    def __init__(self, addr):
        self.server_addr = addr
        self.cur_addr = addr
        self.hostname = 'quackDHCP'
        self.domain = 'quack'

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