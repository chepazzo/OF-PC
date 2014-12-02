from oslo.config.cfg import OptGroup
import ConfigParser
import IPy
from pprint import pprint as pp
 
CONFFILE = 'config/example.cfg'
#CONFFILE = '/etc/pc.conf'

class Conf(object):
    ###
    ## Load Config File
    ###
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
    def load(self,conffile=CONFFILE):
        print "WTF: dnsconf.load({})".format(conffile)
        self.parser.read(conffile)
        print "PCCONF:",dir(self.parser)
        if 'homenet' in self.parser.options('GLOBAL'):
            HOMENET = build_net_tuple(self.parser.get('GLOBAL', 'HOMENET'))
        if 'filternet' in self.parser.options('GLOBAL'):
            FILTERNET = build_net_tuple(self.parser.get('GLOBAL','FILTERNET'))
        pp(self.parser.options('GLOBAL'))
        for sectname in self.parser.sections():
            section = Section(sectname)
            setattr(self,sectname,section)
            for opt in self.parser.options(sectname):
               setattr(section,opt,self.parser.get(sectname,opt))

class Section(object):
    def __init__(self,name):
        self._name = name

def build_net_tuple(net):
    ip = IPy.IP(net)
    return (str(ip.net()),str(ip.netmask()))

def build_rules():
    rules = []
    for section in PCCONF.sections():
        if section == 'GLOBAL': continue
        rule = {
            'src_ip' : section,
            'dow' : (int(d) for d in PCCONF.get(section,'dow').split(',')),
            'time_start' : PCCONF.get(section,'time_start'),
            'time_end' : PCCONF.get(section,'time_end'),
            'dst_str' : PCCONF.get(section,'dst_str'),
            'action' : PCCONF.get(section,'action'),
        }
        rules.append(rule)
    return rules

settings = Conf()
