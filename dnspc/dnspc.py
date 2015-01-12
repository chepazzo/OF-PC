# coding=utf-8
import socket
import copy,sys

## date and time
import time
import datetime
from dateutil.parser import parse as dateparse

## DNS stuff
from dnslib import DNSRecord,RR,QTYPE,RCODE,parse_time
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger
from dnslib.proxy import ProxyResolver,PassthroughDNSHandler,DNSHandler

## DNSPC stuff
import utils.misc
from dnsconf import settings

## Candy
from pprint import pprint as pp

class DataObj(object):
    def __init__(self,**kwargs):
        self._uid = None
        for k in kwargs:
            setattr(self,k,kwargs[k])
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

class PCRule(DataObj):
    def __init__(self,**kwargs):
        self.src_ip = '*'
        self.dst_str = '*'
        self.dow = []
        self.time_start = '0:00'
        self.time_end = '11:59'
        self.action = 'block'
        self.redirect = None
        super(PCRule, self).__init__(**kwargs)
        self.src_name = get_name_from_ip(self.src_ip)
    def is_match(self,src_ip=None,dst_str=None):
        if src_ip != self.src_ip:
            return False
        if not dst_str.matchGlob(self.dst_str):
            return False
        ## Does this rule apply to today?
        if len(self.dow) > 0:
            if utils.misc.get_dow() not in self.dow:
                return False
        ## It applies to today, but what about right now?
        now = datetime.datetime.now().time()
        time_start = dateparse('0:0').time()
        time_end = dateparse('23:00:00').time()
        ## Create datetime.time objects from PCRule
        if self.time_start not in ['','*']:
            time_start = dateparse(self.time_start).time()
        if self.time_end not in ['','*']:
            time_end = dateparse(self.time_end).time()
        if now < time_start:
            return False
        if time_end < now:
            return False
        return True

class PCHost(DataObj):
    def __init__(self,**kwargs):
        self.name = None
        self.ip = None
        self.mac = None
        self.owner = None
        super(PCHost, self).__init__(**kwargs)
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
        self.hosts = []
        self.LOCAL_IP = settings.DNS['LOCAL_IP']
        self.LOCAL_PORT = settings.DNS['LOCAL_PORT']
        self.UP_IP = settings.DNS['UP_IP']
        self.UP_PORT = settings.DNS['UP_PORT']
        self.TCP = settings.DNS['TCP']
        self.TTL = parse_time(settings.DNS['TTL'])
        self.store ={
            'rules': settings.DATA['RULES'],
            'hosts': settings.DATA['HOSTS']
        }
        self.load_rules()
        self.load_hosts()

    ## Rules
    def load_rules(self):
        stored_rules = self.store['rules'].loadRecords()
        uids = [r['_uid'] for r in self.rules]
        for sr in stored_rules:
            if sr['_uid'] in uids:
                continue
            rule = PCRule(**sr)
            self.rules.append(rule)
        print "WTF:rules:",self.rules
    def update_rule(self,rule):
        uid = rule._uid
        idxs = [i for i,c in enumerate(self.rules) if c._uid == uid]
        if len(idxs) == 0:
            self.rules.append(rule)
        else:
            self.rules[idxs[0]] = rule
        return rule

    def save_rule(self,d=None,**kwargs):
        #print "save_rule({})".format(kwargs)
        ## Remove angularjs artifacts:
        kwargs.pop('$$hashKey',None)
        saved_rule = self.store['rules'].editRecord(kwargs)
        print "WTF: saved_rule:",saved_rule
        rule = PCRule(**saved_rule)
        ## Not sure if I should update the rule, or just reload from disk.
        self.update_rule(rule)
        return rule

    def del_rule(self,uid):
        ''' del_rule(uid) returns:
             None: uid did not appear in list.
             True: success
            False: failure
        '''
        #print "del_rule({})".format(uid)
        #pp([x._serialize() for x in self.rules])
        self.store['rules'].deleteRecord({'_uid':uid})
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

    ## Hosts
    def load_hosts(self):
        stored_hosts = self.store['hosts'].loadRecords()
        uids = [r['_uid'] for r in self.hosts]
        for sr in stored_hosts:
            if sr['_uid'] in uids:
                continue
            rule = PCHost(**sr)
            self.hosts.append(rule)
    def update_host(self,host):
        uid = host._uid
        idxs = [i for i,c in enumerate(self.hosts) if c._uid == uid]
        if len(idxs) == 0:
            self.hosts.append(host)
        else:
            self.hosts[idxs[0]] = host
        return host

    def save_host(self,d=None,**kwargs):
        #print "save_host({})".format(kwargs)
        ## Key generated by filestore.
        ## Can't risk overlap.
        #key = self._genkey(self.hosts)
        #print "WTF: Created key:",key
        kwargs.pop('$$hashKey',None)
        saved_host = self.store['hosts'].editRecord(kwargs)
        print "WTF: saved_host:",saved_host
        host = PCHost(**saved_host)
        self.update_host(host)
        #pp(self.hosts)
        return host

    def del_host(self,uid):
        ''' del_host(uid) returns:
             None: uid did not appear in list.
             True: success
            False: failure
        '''
        #print "del_host({})".format(uid)
        #pp([x._serialize() for x in self.hosts])
        self.store['hosts'].deleteRecord({'_uid':uid})
        if uid not in [x._uid for x in self.hosts]:
            return None
        self.hosts = [x for x in self.hosts if x._uid != uid]
        if uid in [x._uid for x in self.hosts]:
            return False
        return True

    def get_hosts(self):
        return self.hosts

    def _genkey(self,st):
        #print "WTF: _genkey()"
        key = int(time.strftime('%Y%U%w000'))
        #print "WTF: My key:",key
        keys = [r._uid for r in st]
        #print "WTF: keys:",keys
        #while len([1 for r in st if int(r['_uid']) == key]) > 0:
        while key in keys:
            key = key + 1
        return key

    ## DNS Server Methods
    def start(self):
        handler = DNSHandler
        # log options: "recv,send,request,reply,truncated,error,data"
        # log defaults: "request,reply,truncated,error"
        # It's just too much stuff!
        logger = DNSLogger("truncated,error",True)
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
            ## Collecting info on match for logging
            match_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            match_name = client_ip
            match_hosts = [h.name for h in self.hosts if h.ip == client_ip]
            if any(match_hosts):
                match_name = ",".join(match_hosts)
            for rule in rules:
                if rule.action == 'redirect':
                    print "[{}] REDIRECT {}-->{} to {}".format(match_time,match_name,qname,rule.redirect)
                    redir = rule.redirect
                    reply.add_answer(*RR.fromZone("{} IN A {}".format(qname,redir)))
                    return reply
                if rule.action == 'block':
                    print "[{}] BLOCKED {}({})-->{}".format(match_time,match_name,client_ip,qname)
                    return reply
                if rule.action == 'allow':
                    print "[{}] ALLOWED {}({})-->{}".format(match_time,match_name,client_ip,qname)
        ## If no match or action == 'allow', then proxy the request to IP_UP
        if handler.protocol == 'udp':
            proxy_r = request.send(self.UP_IP,self.UP_PORT)
        else:
            proxy_r = request.send(self.UP_IP,self.UP_PORT,tcp=True)
        reply = DNSRecord.parse(proxy_r)
        return reply

def get_name_from_ip(ip):
    fs = settings.DATA['HOSTS']
    rec = fs.findRecord('ip',ip)
    if rec is not None:
        return rec['name']
    name = socket.getfqdn(ip)
    if name == ip:
        return ip
    return name.split('.')[0]

if __name__ == '__main__':
    PC = ParentalControls()
    print PC
    PC.start()

