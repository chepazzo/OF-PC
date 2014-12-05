#!/usr/bin/env python
import sys
import argparse
from dnspc import dnsconf

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",default='/etc/dnspc.conf',help="Specify config file")
    parser.add_argument('--debug', action='store_true', default=False,help="Enable debug mode")
    args = parser.parse_args()

    if args.debug is True:
        print "Flask DEBUG"
    else:
        print "Flask Production"

    settings = dnsconf.settings
    settings.load(args.i)
    from dnspc import server
    from dnspc import dnspc
    print "About to start PC"
    #server.PC.start()

    print "About to start flask"
    server.app.run(host=settings.WEB['HOST'],port=settings.WEB['PORT'],debug = settings.WEB['DEBUG'])
    ## Nothing else gets executed here

if __name__ == '__main__':
    main()
