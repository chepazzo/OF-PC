import time
import socket
import datetime

from .events import timer
from . import conf

from ryu.lib import hub
from ryu.lib import packet
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.controller import ofp_event
from ryu.controller import (dpset, event)
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import set_ev_handler

VLAN = packet.vlan.vlan.__name__
IPV4 = packet.ipv4.ipv4.__name__
IPV6 = packet.ipv6.ipv6.__name__
ARP = packet.arp.arp.__name__
ICMP = packet.icmp.icmp.__name__
TCP = packet.tcp.tcp.__name__
UDP = packet.udp.udp.__name__

from ryu.app.wsgi import WSGIApplication

class ParentalControls(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    #_CONTEXTS = {'dpset': dpset.DPSet }
    _CONTEXTS = {'wsgi': WSGIApplication }

    ## Create Events that this app will generate
    class _EventSayHi(event.EventBase):
        pass
    ## Create event handlers for events
    @set_ev_handler(_EventSayHi, MAIN_DISPATCHER)
    def say_hi_handler(self, ev):
        print "event!"
        self.say_hi(ev)

    def __init__(self, *args, **kwargs):
        super(ParentalControls, self).__init__(*args, **kwargs)
        #self.dpset = kwargs['dpset']

    ## Things to do after this app loads
    def start(self,*args, **kwargs):
        super(ParentalControls, self).start(*args, **kwargs)
        print "starting ParentalControls"
        ## Create timer to fire Event after interval
        ## Leaving this as an example in case I want to do this
        #self.register_observer(self._EventSayHi, self.name)
        #self.sayhitimer = timer.TimerEventSender(self, self._EventSayHi)
        #self.sayhitimer.start(5)

    ## Things to do when a Switch has registered features
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        ## Add Base Flow to forward normally
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)
        ## Add Base Flow to forward homenet-homenet packets normally
        if 'HOMENET' in dir(conf):
            match = parser.OFPMatch(
                eth_type=ether.ETH_TYPE_IP,
                ipv4_src=conf.HOMENET,
                ipv4_dst=conf.HOMENET,
            )
            actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL,
                                            ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(dp, 1, match, actions)
        ## Add Base Flow to forward packets matching specific host to the controller
        if 'FILTERNET' in dir(conf):
            match = parser.OFPMatch(
                eth_type=ether.ETH_TYPE_IP,
                ipv4_src=conf.FILTERNET,
            )
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                            ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(dp, 1, match, actions)

    def add_flow(self, dp, priority, match, actions):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        ##  When a packet comes in, I want to check the src_ip and dst_ip
        ##  for a matching config for the current time.
        ##  If there is no or Whitelist match, add a flow that lasts 1h for the src+dst to NORMAL
        ##  If there is a Blacklist match, add a flow that lasts for 1h for the src+dst to DROP
        msg = ev.msg
        print "I Got A Packet!"
        dp = msg.datapath
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        pkt = packet.packet.Packet(msg.data)
        eth = pkt.get_protocol(packet.ethernet.ethernet)
        header_list = dict((p.protocol_name, p)
                           for p in pkt.protocols if type(p) != str)
        (src_ip,dst_ip) = self.get_pktips(header_list)
        src_host = socket.getfqdn(src_ip)
        dst_host = socket.getfqdn(dst_ip)
        #try:
        #    src_host = socket.gethostbyaddr(src_ip)
        #except:
        #    pass
        #try:
        #    dst_host = socket.gethostbyaddr(dst_ip)
        #except:
        #    pass
        print "    %s --> %s"%(src_ip,dst_ip)
        print "    %s --> %s"%(src_host,dst_host)
        matches = 0
        for rule in conf.RULES:
            if not self.is_rule_for_now(rule):
                print "RULE not for now"
                continue
            if rule['src_ip'] != str(src_ip):
                print "RULE src_ip doesn't match packet"
                continue
            #dst_host = ''
            #try:
            #    dst_host = socket.gethostbyaddr(dst_ip)[0]
            #except:
            #    continue
            if rule['dst_str'] not in dst_host:
                print "RULE dst_host (%s) doesn't match packet (%s)"%(rule['dst_str'],dst_host)
                continue
            #src_host = socket.gethostbyaddr(src_ip)
            #if rule['src_str'] not in src_host:
            #    continue
            match = parser.OFPMatch(
                eth_type=ether.ETH_TYPE_IP,
                ipv4_src=(src_ip,'255.255.255.255'),
                ipv4_dst=(dst_ip,'255.255.255.255'),
            )
            actions = [] ## empty action list == drop packet
            print "\nSending Rule\n"
            self.add_flow(dp, 3, match, actions)
            matches += 1
        if matches < 1:
            match = parser.OFPMatch(
                    eth_type=ether.ETH_TYPE_IP,
                    ipv4_src=(src_ip,'255.255.255.255'),
                    ipv4_dst=(dst_ip,'255.255.255.255'),
                )
            actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL,
                                            ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(dp, 1, match, actions)

    def get_pktips(self,header_list):
        src_ip = None
        dst_ip = None
        if IPV4 in header_list:
            src_ip = header_list[IPV4].src
            dst_ip = header_list[IPV4].dst
        elif IPV6 in header_list:
            src_ip = None #header_list[IPV6].src
            dst_ip = None #header_list[IPV6].dst
        elif ARP in header_list:
            src_ip = header_list[ARP].src_ip
            dst_ip = header_list[ARP].dst_ip
        return (src_ip,dst_ip)

    def is_rule_for_now(self,rule):
        now = datetime.datetime.now()
        dow = now.weekday()
        days = rule['dow']
        if dow not in days:
            print "RULE dow does not match"
            return False
        st = [int(t) for t in rule['time_start'].split(':')]
        start = datetime.time(*st)
        if start > now.time():
            print "RULE start > now"
            return False
        et = [int(t) for t in rule['time_end'].split(':')]
        end = datetime.time(*et)
        if end < now.time():
            print "RULE end < now"
            return False
        return True

    @set_ev_cls(dpset.EventDP, MAIN_DISPATCHER)
    def dp_handler(self, ev):
        dpid = ev.dp.id
        if ev.enter:
            print "switch %s just entered (%s)"%(dpid,ev.dp.address)
            ports = set((port.port_no,port.name,port.config) for port in ev.ports)
            for port in ports:
                print "    Port %s:%s"%(port[1],port[0])

    ## This was here when the Timer event wasn't firing
    ## I prob shouldn't do it this way and should prob
    ## just remove this code.
    ## This would be invoked with:
    ##    self.threads.append(hub.spawn(self.loop_hi))
    #def loop_hi(self):
    #    while True:
    #        print "Howdy!"
    #        time.sleep(5)

