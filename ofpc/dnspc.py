# coding=utf-8
import time
import copy,sys
from dnslib import DNSRecord,RR,QTYPE,RCODE,parse_time
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger
from dnslib.proxy import ProxyResolver,PassthroughDNSHandler,DNSHandler

#from . import dnsconf

class ParentalControls(object):

    def __init__(self):
        self.rules = []
        self.load_from_config()

    def load_from_config(self):
        ## Change to load from saved config
        self.LOCAL_IP = '127.0.0.1'
        self.LOCAL_PORT = 53
        #self.UP_IP = '127.0.1.1'
        self.UP_IP = '8.8.8.8'
        self.UP_PORT = 53
        self.TCP = True

    def start_dnsserver(self):
        self.resolver = InterceptResolver(self.UP_IP,self.UP_PORT,'60s',
            [
                #Need to load from dnsconfig
            ],[],[])
        #handler = PassthroughDNSHandler
        handler = DNSHandler
        logger = DNSLogger("request,reply,truncated,error",False)
        self.udp_server = DNSServer(self.resolver,
                            port=self.LOCAL_PORT,
                            address=self.LOCAL_IP,
                            logger=logger,
                            handler=handler)
        for rr in self.resolver.zone:
            print "    | ",rr[2].toZone()
        if self.resolver.nxdomain:
            print "    NXDOMAIN:",", ".join(self.resolver.nxdomain)
        if self.resolver.skip:
            print "    Skipping:",", ".join(self.resolver.skip)
        print
        self.udp_server.start_thread()
        if self.TCP:
            self.tcp_server = DNSServer(self.resolver,
                                port=self.LOCAL_PORT,
                                address=self.LOCAL_IP,
                                tcp=True,
                                logger=logger,
                                handler=handler)
            self.tcp_server.start_thread()
        #self.resolver.add_zone('*.bakeshutwait.com IN A 10.15.201.53')
        #while udp_server.isAlive():
        #    time.sleep(1)

    def stop_dnsserver(self):
        self.udp_server.stop()
        if self.TCP:
            self.tcp_server.stop()

    def add_rule(self,d=None,**kwargs):
        self.rules.append(PCRule(**kwargs))

    def get_rules(self):
        return self.rules

## note to self: change from object to dict later
class PCRule(object):
    def __init__(self,**kwargs):
        self.src_ip = kwargs['src_ip']
        self.dow = kwargs['dow']
        self.time_start = kwargs['time_start']
        self.time_end = kwargs['time_end']
        self.dst_str = kwargs['dst_str']
        self.action = kwargs['action']

class InterceptResolver(BaseResolver):

    """
        Intercepting resolver 
        
        Proxy requests to upstream server optionally intercepting requests
        matching local records
    """

    def __init__(self,address,port,ttl,intercept,skip,nxdomain):
        """
            address/port    - upstream server
            ttl             - default ttl for intercept records
            intercept       - list of wildcard RRs to respond to (zone format)
            skip            - list of wildcard labels to skip 
            nxdomain        - list of wildcard labels to retudn NXDOMAIN
        """
        self.address = address
        self.port = port
        self.ttl = parse_time(ttl)
        self.skip = skip
        self.nxdomain = nxdomain
        self.zone = []
        for i in intercept:
            if i == '-':
                i = sys.stdin.read()
            for rr in RR.fromZone(i,ttl=self.ttl):
                self.zone.append((rr.rname,QTYPE[rr.rtype],rr))

    def add_zone(self,zone):
        print "Adding Zone: {}".format(zone)
        for rr in RR.fromZone(zone,ttl=self.ttl):
            self.zone.append((rr.rname,QTYPE[rr.rtype],rr))
        print self.zone

    def resolve(self,request,handler):
        client_ip = handler.client_address
        print "Request from IP: {}".format(client_ip)
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        # Try to resolve locally unless on skip list
        if not any([qname.matchGlob(s) for s in self.skip]):
            for name,rtype,rr in self.zone:
                if qname.matchGlob(name) and (qtype in (rtype,'ANY','CNAME')):
                    a = copy.copy(rr)
                    a.rname = qname
                    reply.add_answer(a)
        # Check for NXDOMAIN
        if any([qname.matchGlob(s) for s in self.nxdomain]):
            reply.header.rcode = getattr(RCODE,'NXDOMAIN')
            return reply
        # Otherwise proxy
        if not reply.rr:
            if handler.protocol == 'udp':
                proxy_r = request.send(self.address,self.port)
            else:
                proxy_r = request.send(self.address,self.port,tcp=True)
            reply = DNSRecord.parse(proxy_r)
        return reply

if __name__ == '__main__':
    PC = ParentalControls()
    print PC
    PC.start_dnsserver()

