# -*- coding: utf-8 -*-

__author__ = 'Mike Biancaniello <mikebianc@aol.com>'
__version__ = 'Revision '
# Source 

import json
import os.path
import time

class FileStore(object):

 def __init__(self):
    self.keyfield = '_uid'
    self.filename = ''
    self.recArr = []

 def setKeyField(self,keyfield):
    if not keyfield:
        return self
    self.keyfield = keyfield
    return self

 def getKeyField(self):
    return self.keyfield

 def setFilename(self,filename):
    if not filename:
        return self
    self.filename = filename
    return self

 def getFilename(self):
    return self.filename

 def getRecords(self,isarr=0):
    if not len(self.recArr):
        self.loadRecords()
    return self.recArr

 def loadRecords(self):
    fname = self.getFilename()
    farr = []
    if not os.path.exists(fname):
        return []
    with open(fname,'r') as fr:
        farr = fr.readlines()
    self.recArr = [json.loads(line) for line in farr]
    return self.recArr

 def toXML(self):
    return self

 def findRecords(self,path,value):
    retarr    = []
    records    = self.getRecords()
    for record in records:
        if self.isMatch(record,path,value,0):
            retarr.append(record)
    return retarr

 def findRecord(self,path,value):
    records    = self.getRecords()
    for record in records:
        if self.isMatch(record,path,value,0):
            return record
    return None

 def searchRecords(self,path,value):
    retarr    = []
    records    = self.getRecords()
    for record in records:
        if self.isMatch(record,path,value,1):
            retarr.append(record)
    return retarr

 def isMatch(self,obj,path,value,substr=0):
   if not obj:
     return
   match = 0
   if isinstance(obj,list):
       for arrobj in obj:
           match = self.isMatch(arrobj,path,value,substr)
           if match:
             return 1
       return 0
   elif isinstance(obj,dict):
       pieces = path.split('.')
       piece = pieces.pop(0)
       path = '.'.join(pieces)
       ## NEED TO TEST FOR EXISTANCE OF obj[pieces] first, o.w. IT THROWS AN ERROR
       obj = obj[piece]
       match = self.isMatch(obj,path,value,substr)
       if match:
         return 1
   else:
       if obj == value:
         return 1
       return 0
   return 0


 def deleteRecord(self,newrecord):
    success = 0
    keyfield    = self.getKeyField()
    newkey    = newrecord[keyfield]
    if not newkey:
        return 0
    records = self.getRecords()
    fname = self.getFilename();
    if not os.path.exists(fname):
        return 0
    with open(self.getFilename(), "w") as fw:
        for record in records:
            if record[keyfield] != newkey:
                fw.write(json.dumps(record)+"\n")
            else:
                success = 1
    self.loadRecords()
    if success:
        return newrecord
    else:
        return 0


 def addRecord(self,newrecord):
    keyfield = self.keyfield
    key = int(time.strftime('%Y%U%w000'))
    fname = self.getFilename()
    farr = self.getRecords()
    """
    Make sure that this key is unique!
    Since we are just appending to the file, we need
    to make sure that if the newrecord already had a key, 
    we don't create 2 records with the same key!!!
    """
    while len([1 for record in farr if record[self.keyfield] == str(key)]) > 0:
        key = key + 1
    newrecord[keyfield] = str(key)
    with open(self.getFilename(), "a") as fa:
        fa.write(json.dumps(newrecord)+"\n")
    self.loadRecords()
    return newrecord


 def editRecord(self,newrecord):
    success = 0
    keyfield    = self.getKeyField()
    newkey    = newrecord.get(keyfield,None)
    if not newkey:
        """
        If no key in new record data, then append as a new record
        """
        return self.addRecord(newrecord)
    fname = self.getFilename();
    if not os.path.exists(fname):
        return 0
    # Load fresh copy of records in case something was added since the last grab.
    #  There is still a race condition, though.
    records = self.loadRecords()
    with open(fname, "w") as fw:
        for record in records:
            if record[keyfield] == newkey:
                record = newrecord
                success = 1
            fw.write(json.dumps(record)+"\n")
    self.loadRecords()
    if success:
        return newrecord
    else:
        return 0

