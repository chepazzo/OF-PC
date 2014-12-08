# coding=utf-8
import time
import socket
import copy,sys
from dnslib import DNSRecord,RR,QTYPE,RCODE,parse_time
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger
from dnslib.proxy import ProxyResolver,PassthroughDNSHandler,DNSHandler
from pprint import pprint as pp

from dnsconf import settings

class PCRule(object):
    def __init__(self,**kwargs):
        self.src_ip = '*'
        self.dst_str = '*'
        self.dow = '*'
        self.time_start = '*'
        self.time_end = '*'
        self.action = 'block'
        self.redirect = settings.DNS['REDIRECT']
        #print "WTF: PCRule()"
        for k in kwargs:
            setattr(self,k,kwargs[k])
        self.src_name = socket.getfqdn(self.src_ip)
    def is_match(self,src_ip=None,dst_str=None):
        ## put in a for loop to verify each value is a match
        #print "does {} from {} match {} from {}".format(dst_str,src_ip,self.dst_str,self.src_ip)
        #print type(src_ip)
        if src_ip != self.src_ip:
            #print "    NO (IP)!"
            return False
        if not dst_str.matchGlob(self.dst_str):
            #print "    NO (Domain)!"
            return False
        #print "    YES!"
        return True
    def _serialize(self,fields=None,skip=None):
        retval = {}
        if fields is None:
            fields = self.__dict__.keys()
        if skip is None:
            skip = []
        for f in fields:
            if f in skip:
                continue
            retval[f] = getattr(self,f,None)
        return retval


class ParentalControls(BaseResolver):

    """
        Intercepting resolver 
        
        Proxy requests to upstream server optionally intercepting requests
        matching local records
    """

    def __init__(self):
        self.rules = []
        self.LOCAL_IP = settings.DNS['LOCAL_IP']
        self.LOCAL_PORT = settings.DNS['LOCAL_PORT']
        self.UP_IP = settings.DNS['UP_IP']
        self.UP_PORT = settings.DNS['UP_PORT']
        self.TCP = settings.DNS['TCP']
        self.TTL = parse_time(settings.DNS['TTL'])

    def start(self):
        handler = DNSHandler
        logger = DNSLogger("request,reply,truncated,error",False)
        print "Starting UDP server"
        if 'udp_server' not in dir(self):
            self.udp_server = DNSServer(self,
                            port=self.LOCAL_PORT,
                            address=self.LOCAL_IP,
                            logger=logger,
                            handler=handler)
        self.udp_server.start_thread()
        if self.TCP:
            print "Starting TCP server"
            if 'tcp_server' not in dir(self):
                self.tcp_server = DNSServer(self,
                                port=self.LOCAL_PORT,
                                address=self.LOCAL_IP,
                                tcp=True,
                                logger=logger,
                                handler=handler)
            self.tcp_server.start_thread()

    def stop(self):
        print dir(self)
        if 'udp_server' in dir(self):
            print "    Stopping UDP server."
            self.udp_server.stop()
        if 'tcp_server' in dir(self) and self.TCP:
            print "    Stopping TCP server."
            self.tcp_server.stop()

    def add_rule(self,d=None,**kwargs):
        #print "add_rule({})".format(kwargs)
        #pp(kwargs)
        key = self._genkey()
        #print "WTF: Created key:",key
        rule = PCRule(_uid=key,**kwargs)
        #print "rules are cool"
        self.rules.append(rule)
        #pp(self.rules)
        return rule

    def del_rule(self,uid):
        ''' del_rule(uid) returns:
             None: uid did not appear in list.
             True: success
            False: failure
        '''
        #print "del_rule({})".format(uid)
        #pp([x._serialize() for x in self.rules])
        uids = [x._uid for x in self.rules]
        #print uids
        if uid not in [x._uid for x in self.rules]:
            return None
        self.rules = [x for x in self.rules if x._uid != uid]
        if uid in [x._uid for x in self.rules]:
            return False
        return True

    def get_rules(self):
        return self.rules

    def get_matching_rules(self,src_ip,dst_str):
        rs = [ r for r in self.rules if r.is_match(src_ip,dst_str) ]
        return rs

    def _genkey(self):
        #print "WTF: _genkey()"
        key = int(time.strftime('%Y%U%w000'))
        #print "WTF: My key:",key
        keys = [r._uid for r in self.rules]
        #print "WTF: keys:",keys
        #while len([1 for r in self.rules if int(r['_uid']) == key]) > 0:
        while key in keys:
            key = key + 1
        return key

    def resolve(self,request,handler):
        client_ip = handler.client_address[0]
        #print "Request from IP: {}".format(client_ip)
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        #print "query: {}".format(qname)
        #print "query: {}".format(qname.matchGlob("*.yahoo.com"))
        # Try to resolve locally unless on skip list
        rules = self.get_matching_rules(client_ip,qname)
        if any(rules):
            print "Matched Rules:",[ r.__dict__ for r in rules ]
            ## right now returning nothing
            ## need to change to return based on rule match
            ## (block, redirect, etc)
            for rule in rules:
                if rule.action == 'redirect':
                    print "Redirecting",qname,"to:",rule.redirect
                    redir = rule.redirect
                    reply.add_answer(*RR.fromZone("{} IN A {}".format(qname,redir)))
                if rule.action == 'block':
                    print "Blocking",qname
                    return reply
        else:
            ## If no match, then proxy the request to IP_UP
            if handler.protocol == 'udp':
                proxy_r = request.send(self.UP_IP,self.UP_PORT)
            else:
                proxy_r = request.send(self.UP_IP,self.UP_PORT,tcp=True)
            reply = DNSRecord.parse(proxy_r)
        return reply

if __name__ == '__main__':
    PC = ParentalControls()
    print PC
    PC.start()

