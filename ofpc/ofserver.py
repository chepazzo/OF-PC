#/usr/bin/env python

## Add rule to ruleset via POST to /addrule:
## curl -i -H "Content-Type: application/json" -X POST -d '{"mac":"192.168.0.134","dow":"0,1,2,3,4","time_start":"18:00","time_end:"23:59","domain":"youtube.com","action":"block"}' http://localhost:5000/addrule

from flask import Flask, render_template, request
app = Flask(__name__)

import dnspc
import os
import json
from pprint import pprint as pp

PC = dnspc.ParentalControls()

@app.route('/')
def top():
    return "MISHAP ParentalControls!"

@app.route('/index.html')
def index():
    return render_template('index.html',
        list=list,
        json=json,
        currrules=PC.rules)

@app.route('/start')
def start():
    PC.start_dnsserver()
    return "OFPC Started!"

@app.route('/stop')
def stop():
    PC.stop_dnsserver()
    return "OFPC Stopped!"

@app.route('/addfart', methods = ['POST'])
def addfart():
    #pp(request.__dict__)
    #pp(dir(request))
    print "oh?: {}".format(request.json.get('src_ip',None))
    rule = PC.add_rule(**request.json)
    #PC.restart_pc()
    return json.dumps(request.json)
    #return "added {}".format(rule._serialize())

@app.route('/get/rules')
def get_rules():
    rules = PC.get_rules()
    print 'rules',rules
    #return "my rules\n"
    retval = [s._serialize() for s in PC.rules]
    return json.dumps(retval)

if __name__ == '__main__':
    import sys
    if 'debug' in sys.argv:
        print "Flask DEBUG"
        app.run(debug = True)
    else:
        print "Flask Production"
        app.run(host='0.0.0.0')
    PC.start_dnsserver()

