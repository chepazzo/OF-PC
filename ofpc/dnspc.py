# coding=utf-8
import time
import copy,sys
from dnslib import DNSRecord,RR,QTYPE,RCODE,parse_time
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger
from dnslib.proxy import ProxyResolver,PassthroughDNSHandler,DNSHandler

from . import dnsconf

LOCAL_IP = '127.0.0.1'
LOCAL_PORT = 53
UP_IP = '127.0.1.1'
#UP_IP = '8.8.8.8'
UP_PORT = 53
TCP = True

def main():
    resolver = InterceptResolver(UP_IP,UP_PORT,'60s',
        [
            '*.bakeshutwait.com IN A 10.15.201.53'
        ],[],[])
    #handler = PassthroughDNSHandler
    handler = DNSHandler
    logger = DNSLogger("request,reply,truncated,error",False)
    udp_server = DNSServer(resolver,
                           port=LOCAL_PORT,
                           address=LOCAL_IP,
                           logger=logger,
                           handler=handler)
    for rr in resolver.zone:
        print "    | ",rr[2].toZone()
    if resolver.nxdomain:
        print "    NXDOMAIN:",", ".join(resolver.nxdomain)
    if resolver.skip:
        print "    Skipping:",", ".join(resolver.skip)
    print
    udp_server.start_thread()
    if TCP:
        tcp_server = DNSServer(resolver,
                               port=LOCAL_PORT,
                               address=LOCAL_IP,
                               tcp=True,
                               logger=logger,
                               handler=handler)
        tcp_server.start_thread()
    while udp_server.isAlive():
        time.sleep(1)

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

    def resolve(self,request,handler):
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
    main()

