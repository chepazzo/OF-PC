
import os
import netaddr
import socket

def get_hostname(ip):
    name = socket.getfqdn(ip)
    if name == ip:
        return ip
    return name.split('.')[0]

def get_mac_addr(ip,ping=False):
    if ping:
        os.popen("ping -c1 -W1 -qn %s > /dev/null"%ip)
    cmd = "arp -n %s|awk '/%s/ {print $3}'"%(ip,ip)
    mac = os.popen(cmd).read().strip() or None
    return parse_MAC(mac)

def parse_MAC(addr):
    try:
        mac = netaddr.EUI(addr)
    except netaddr.core.AddrFormatError:
        return None
    mac.dialect = netaddr.mac_unix
    return mac

