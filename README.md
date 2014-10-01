OF-PC
=====

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

OVS Setup
---------

***Caution: If you do this wrong, you will lose access to the Internet and subsequently your ability to find a solution to fix it***

You should just need to install the openvswitch-switch package for your distribution. Make sure that the binaries for ovs-vsctl and ovs-ofctl exist on your system. 

Keep in mind that (despite the configuration) OVS is a switch, not an interface. Once you have installed the switch, you need to connect interfaces to it. In this example, I am going to create a vswitch named ovsbr0 and attach eth0 as an L2 interface. The IP address (via DHCP) will be configured on a new L3 interface named (creatively) l3port. These interfaces are created and attached to the vswitch with the ovs-vsctl tool, which stores this data in an ovsdb for persistance on reboot. Configuration of the interfaces can be done with the route command and stored in /etc/network/interfaces (or the equivalent on your system). 

***Connect the interfaces to your switch***

    ovs-vsctl init
    ovs-vsctl add-br ovsbr0
    ovs-vsctl add-port ovsbr0 l3port
    ovs-vsctl add-port ovsbr0 eth0
    ovs-vsctl set bridge ovsbr0 protocols=OpenFlow13

**Display results**

    # ovs-vsctl list-br
    ovsbr0
    # ovs-vsctl list-ports ovsbr0
    eth0
    l3port

***Configure /etc/network/interfaces:***

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
    
    auto eth0
    auto l3port

***Enable Interfaces***

    ifup eth0
    ifup l3port

**Display**

    # ovs-vsctl show
    1d391ad6-7da1-407f-a469-2a5ac910f915
        Bridge "ovsbr0"
            Port "ovsbr0"
                Interface "ovsbr0"
                    type: internal
            Port "eth0"
                Interface "eth0"
            Port "l3port"
                Interface "l3port"
                    type: internal
        ovs_version: "1.10.2"


###See Also
* http://git.openvswitch.org/cgi-bin/gitweb.cgi?p=openvswitch;a=blob_plain;f=WHY-OVS;hb=HEAD
* http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-controller.8
* http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-vsctl.8
* http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-ofctl.8
 
You should also install wireshark, which doesn't come with an of-dissector, so you will have to grab this one:

    git clone https://github.com/CPqD/ofdissector 

