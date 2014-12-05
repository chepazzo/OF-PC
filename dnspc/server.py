#/usr/bin/env python

## Add rule to ruleset via POST to /addrule:
## curl -i -H "Content-Type: application/json" -X POST -d '{"mac":"192.168.0.134","dow":"0,1,2,3,4","time_start":"18:00","time_end:"23:59","domain":"youtube.com","action":"block"}' http://localhost:5000/addrule

from flask import Flask, render_template, request
app = Flask(__name__)

import dnspc
from dnsconf import settings
import os
import json
from pprint import pprint as pp

PC = dnspc.ParentalControls()

@app.route('/')
#def top():
#    return "MISHAP ParentalControls!"
#
#@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/addrule.html')
def addrulehtml():
    return render_template('addrule.html')

@app.route('/PCCtrl.js')
def pcctrljs():
    return render_template('PCCtrl.js')

@app.route('/start')
def start():
    PC.start()
    return "dnspc Started!"

@app.route('/stop')
def stop():
    PC.stop()
    return "dnspc Stopped!"

@app.route('/addrule', methods = ['POST'])
def addrule():
    rule = PC.add_rule(**request.json)
    return json.dumps(succ(value=rule._serialize()))

@app.route('/delrule', methods = ['POST'])
def delrule():
    args = request.json
    uid = args['uid']
    res = PC.del_rule(uid)
    if res == False:
        ret = fail('Unable to delete rule {}'.format(uid))
    else:
        ret = succ(value=uid)
    return json.dumps(ret)

@app.route('/get/rules')
def get_rules():
    rules = PC.get_rules()
    retval = [s._serialize() for s in PC.rules]
    return json.dumps(succ(value=retval))

def succ(field='data',value=''):
    ''' {'stat':'ok', 'data':{} '''
    return {'stat':'ok',field:value}

def fail(msg='',code=0):
    ''' {'stat':'fail', 'err':{'msg':'', 'code':0}} '''
    err = {'msg':msg,'code':code}
    return {'stat':'fail','err':err}

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",default='/etc/dnspc.conf',help="Specify config file")
    parser.add_argument('--debug', action='store_true', default=False,help="Enable debug mode")
    args = parser.parse_args()

    if args.debug is True:
        print "Flask DEBUG"
    else:
        print "Flask Production"

    print "About to start PC"
    PC.stop()
    PC.start()

    print "About to start flask"
    app.run(host='0.0.0.0',debug = args.debug)
    ## Nothing else gets executed here
