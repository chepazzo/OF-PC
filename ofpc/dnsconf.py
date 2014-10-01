from oslo.config.cfg import OptGroup
import ConfigParser
import IPy
 
CONFFILE = 'config/example.cfg'
#CONFFILE = '/etc/pc.conf'

###
## Load Config File
###
PCCONF = ConfigParser.ConfigParser()
PCCONF.read(CONFFILE)

print "OPTIONS",PCCONF.options('GLOBAL')

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

if 'homenet' in PCCONF.options('GLOBAL'):
    HOMENET = build_net_tuple(PCCONF.get('GLOBAL', 'HOMENET'))
if 'filternet' in PCCONF.options('GLOBAL'):
    FILTERNET = build_net_tuple(PCCONF.get('GLOBAL','FILTERNET'))
RULES=build_rules()

