# -*- coding: utf-8 -*-
import logging
import logging.handlers

LOG_MAIN = '/var/log/dnspc.log'
LOG_MON = '/var/lib/dnspc/monitor.json'

log = logging.getLogger('dnspc')
log.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(LOG_MAIN)
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(fh)

monitor = logging.getLogger('monitor')
monitor.setLevel(logging.DEBUG)
mfh = logging.handlers.RotatingFileHandler(LOG_MON)
mfh.setFormatter(logging.Formatter('%(message)s'))
monitor.addHandler(mfh)

