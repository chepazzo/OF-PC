#!/usr/bin/env python
from ofpc import server
from ofpc import dnspc
from ofpc import dnsconf
import sys
import argparse

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
    print "Settings: ",settings.__dict__
    print "About to start PC"
    server.PC.start()

    print "About to start flask"
    server.app.run(host='0.0.0.0',debug = args.debug)
    ## Nothing else gets executed here

if __name__ == '__main__':
    main()
