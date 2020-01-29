@echo off

::CHANGE THIS TO WHATEVER NETWORK ADAPTER YOU ARE TRYING TO USE
set interface=Ethernet

SET /P server_ip= Enter the server address or none for default (192.168.6.200):

IF [%server_ip%]==[] set server_ip=192.168.6.200

echo Setting %interface% interface to static ip %server_ip%...

netsh interface ip set address %interface% static %server_ip% 255.255.255.0

timeout /t 3 /nobreak

py %~dp0DHCPServer.py %server_ip%

echo Setting %interface% interface back to DHCP...

netsh interface ip set address %interface% dhcp

@pause

