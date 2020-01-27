# dhcpserver
A lightweight DHCP server for configuring devices on a LAN without a temporary router.


How to Use:

-Keep the files in the same folder:

  DHCP.py - Defines the DHCP protocol enough to provide short term DHCP services.
  
  DHCPServer.py - Starts a socket server listening for DHCP requests.
  
  dhcp.bat - Sets a static IP on the ethernet adapter, starts DHCPServer.py, and when the user stops the server, resets the ethernet adapter to DHCP.
  
-If you don't have Python installed, install the latest version of Python from www.python.org/downloads.

-Run dhcp.bat as administrator.

This will provide nice prompts to guide you through, and will also set your ethernet adapter to a static IP for you. When you exit the server, it will set the ethernet adapter back to DHCP. If your ethernet adapter is not named "Ethernet", and you can check this by running ipconfig in the command prompt, you will need to open the .bat file in a text editor and change the name.


Required components:
Python 3
Windows


Testing Environment:
Tested with Windows 10 and Python 3.7.4, and has been tested with the following client devices:

Savant SSC-0012 


Origin/Initial Intent of Project:

The idea for this project came from small audio/video systems whose components communicate via IP, connected by a simple network switch without a router/DHCP server. All the IP addresses are set to static. Most devices have a factory default setting of DHCP, requiring the device to be plugged into a router/DHCP server long enough to log into the device and set a static IP. This would entail the technician carrying a small router with them and plugging it in, along with their computer, to configure the device. If the technician's computer could run a DHCP server though, they could simply plug their PC into the network switch, or directly to the device, and not need another piece of hardware.


LIMITATIONS:

-Is not bound to a specific NIC. For example, if you are connected to the target network via Ethernet and another network via Wi-Fi, the server will respond to DHCP requests on the Wi-Fi network. It will probably not successfully give an IP address to a device on the Wi-Fi network, but it will start incrementing IP addresses, etc.
-Does not check to see if an IP address is already in use. If a client reports that an IP address is already in use, it should attempt to give that client a new address.
-Increments the IPs it hands out every time it gets a new request, starting with the first address after the server address. This means that if you set the server address to 192.168.6.250, it will only had out four addresses before it starts trying to hand out the broadcast address or invalid IP addresses.
-Does not implement the entire DHCP protocol, only the bare minimum to hand out IPs.
-Does very little error handling or validation.
