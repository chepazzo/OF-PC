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
    PC.start()
    return "OFPC Started!"

@app.route('/stop')
def stop():
    PC.stop()
    return "OFPC Stopped!"

@app.route('/addrule', methods = ['POST'])
def addrule():
    #pp(request.__dict__)
    #pp(dir(request))
    #print "oh?: {}".format(request.json.get('src_ip',None))
    rule = PC.add_rule(**request.json)
    #print "rule added!"
    #PC.restart_pc()
    return json.dumps(succ(value=rule._serialize()))
    #return "added {}".format(rule._serialize())

@app.route('/delrule', methods = ['POST'])
def delrule():
    #pp(request.__dict__)
    #pp(dir(request))
    #print "oh?: {}".format(request.json.get('uid',None))
    #pp(request.json)
    args = request.json
    uid = args['uid']
    res = PC.del_rule(uid)
    #print "WTF: uid:",uid,res
    #PC.restart_pc()
    if res == False:
        ret = fail('Unable to delete rule {}'.format(uid))
    else:
        ret = succ(value=uid)
    return json.dumps(ret)
    #return "deleted {}".format(rule._serialize())

@app.route('/get/rules')
def get_rules():
    rules = PC.get_rules()
    #print 'rules',rules
    #return "my rules\n"
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
    if 'debug' in sys.argv:
        print "Flask DEBUG"
        app.run(debug = True)
    else:
        print "Flask Production"
        app.run(host='0.0.0.0')
    PC.start()

