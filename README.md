OF-PControls
============

OpenFlow based parental controls


System Setup
============
First, we need to setup the system where this will run.

1. Configure this server as the default gateway for the clients you want to control.
2. Turn off ICMP Redirects
3. Install Open vSwitch on this server.
4. Configure everything else

Default Gateway
---------------

***Assumptions***

1. None of your network switches support OpenFlow.
    If that is not the case, then you can skip the parts of this that
    are not relevant.

2. You run your own DHCP server somewhere on the network
    This can be on the same machine where you are running this app,
    but it does not have to be.

***DHCP Server***

Configure your DHCP server to set this box as the default gateway for clients 
for which you wish to control access.  I would also suggest that you obtain the
HW ADDRs of these devices and assign them out of a specific range of IPs.  This
way, you will have the option to redirect all flows from these clients to the 
controller in a single flow entry.

Of course, all return traffic *to* these clients will be forwarded directly, bypassing
this server.  There really is no way around this short of installing OF-enabled switches 
or making this a proxy server (and if you were going to do that, then you probably 
would not be installing this OF app).

ICMP Redirects
--------------

Assuming that your network is a single subnet, if you 
keep redirects enabled, your server will tell everyone
else about his own default route (on the same subnet),
and you will stop receiving any egress packets.

**edit: /etc/sysctl.conf**

    net.ipv4.conf.l3port.accept_redirects=1
    net.ipv4.conf.l3port.send_redirects=0
    net.ipv4.conf.all.send_redirects=0
    net.ipv4.ip_forward=1

**bash cmds:**

    /sbin/sysctl -w net.ipv4.conf.l3port.accept_redirects=1
    /sbin/sysctl -w net.ipv4.conf.l3port.send_redirects=0
    /sbin/sysctl -w net.ipv4.conf.all.send_redirects=0

**Add ovs and interfaces**

    ovs-vsctl add-br ovsbr0
    ovs-vsctl add-port ovsbr0 l3port
    ovs-vsctl add-port ovsbr0 eth0

**Display results**

    ovs-vsctl list-br
    ovs-vsctl list-ports ovsbr0

**Bring up interfaces**

    ifup eth0
    ifup l3port
    route -n

***Set OF version to 1.3*** 

    ovs-vsctl set bridge ovsbr0 protocols=OpenFlow13

**/etc/network/interfaces:**

    allow-ovs ovsbr0
    iface ovsbr0 inet manual
        ovs_type OVSBridge
        ovs_ports eth0 l3port
    
    allow-ovsbr0 l3port
    iface l3port inet dhcp
        ovs_bridge ovsbr0
        ovs_type OVSIntPort
    
    allow-ovsbr0 eth0
    iface eth0 inet manual
    ovs_bridge ovsbr0
    ovs_type OVSPort

