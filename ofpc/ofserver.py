#/usr/bin/env python

## Add rule to ruleset via POST to /addrule:
## curl -i -H "Content-Type: application/json" -X POST -d '{"mac":"192.168.0.134","dow":"0,1,2,3,4","time_start":"18:00","time_end:"23:59","domain":"youtube.com","action":"block"}' http://localhost:5000/addrule

from flask import Flask, render_template, request
app = Flask(__name__)

import ofpc
import os
import json
from pprint import pprint as pp

PC = ofpc.ParentalControls()

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
    PC.start_ofpc()
    return "OFPC Started!"

@app.route('/get/rules')
def get_rules():
    retval = [s._serialize() for s in PC.rules]
    return json.dumps(retval)

@app.route('/addrule', methods = ['POST'])
def addrule():
    pp(request.json)
    rule = PC.add_rule(**request.json)
    PC.restart_pc()
    return "added {}".format(rule._serialize())

if __name__ == '__main__':
    import sys
    if 'debug' in sys.argv:
        print "Flask DEBUG"
        app.run(debug = True)
    else:
        print "Flask Production"
        app.run(host='0.0.0.0')

