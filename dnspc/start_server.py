#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger('dnspc.start_server')

import sys
import argparse
#from dnspc import dnsconf
import dnsconf

def main():

    ## Need to load settings before loading other modules
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",default='/etc/dnspc.conf',help="Specify config file")
    parser.add_argument('--debug', action='store_true', default=False,help="Enable debug mode")
    args = parser.parse_args()

    settings = dnsconf.settings
    settings.load(args.i)
    #from dnspc import server
    #from dnspc import dnspc
    import server
    import dnspc

    debug = settings.WEB['DEBUG']

    if args.debug is True:
        debug = True

    if debug:
        logging.getLogger('dnspc').setLevel(logging.DEBUG)
        log.info( "Flask DEBUG" )
    else:
        log.info( "Flask Production" )
        log.info( "Starting PC" )
        server.PC.start()

    log.info( "Starting flask" )
    server.app.run(host=settings.WEB['HOST'],port=settings.WEB['PORT'],debug = debug)
    ## Nothing else gets executed here

if __name__ == '__main__':
    main()
