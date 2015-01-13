from oslo.config.cfg import OptGroup
import ConfigParser
import IPy
from filestore import FileStore
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
        try:
            self.parser.read(conffile)
        except: 
            print "** Conf File ({}) invalid **".format(conffile)
            exit()
        if len(self.parser.sections()) < 1:
            print "** Conf File ({}) missing or invalid **".format(conffile)
            exit()
        for sectname in self.parser.sections():
            section = {}
            setattr(self,sectname,section)
            opts = self.parser.options(sectname)
            for opt in opts:
                val = self.parser.get(sectname,opt)
                if sectname == 'DATA':
                    val = load_datastore(val)
                if opt in ['homenet','filternet']:
                    val = build_net_tuple(val)
                if opt in ['local_port','up_port','port']:
                    val = self.parser.getint(sectname,opt)
                if opt in ['tcp','debug']:
                    val = self.parser.getboolean(sectname,opt)
                section[opt.upper()] =val

def load_datastore(path):
    f = FileStore()
    f.setFilename(path)
    return f

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
