import unittest

import os, sys

dirname = os.path.dirname(os.path.abspath(os.curdir))
if (not any([f == dirname for f in sys.path])):
    print 'Insert "%s" into sys.path.' % (dirname)
    sys.path.insert(0, dirname)

from databaseclient import DatabaseAPI

__url__ = 'http://192.168.1.21:9999'
#__url__ = 'http://127.0.0.1:9192'

class SimpleTestCase1(unittest.TestCase):
    def setUp(self):
	import uuid
	
	self.projectid = str(uuid.uuid4())
	self.db = DatabaseAPI(__url__, project_id=self.projectid)
	pass
	
    def runTest(self):
	self.keyname = 'key1'
	self.keyvalue = 'value1'
	so = self.db.create(self.keyname, self.keyvalue)
	self.assertEqual(str(so.status).upper(), 'SUCCESS')

    def tearDown(self):
	data = self.db.fetch(self.keyname)
	self.assertEqual(data.keyvalue, self.keyvalue)
	data = self.db.delete(keyname=self.keyname)
	self.assertEqual(str(data.status).upper(), 'SUCCESS')
	data = self.db.delete()
	self.assertEqual(str(data.status).upper(), 'SUCCESS')

class SimpleTestCase2(unittest.TestCase):
    def setUp(self):
	import uuid
	
	self.projectid = str(uuid.uuid4())
	self.db = DatabaseAPI(__url__, project_id=self.projectid)
	pass
	
    def runTest(self):
	self.keyname = 'key1'
	self.keyvalue = 'value1'
	so = self.db.create(self.keyname, self.keyvalue)
	self.assertEqual(str(so.status).upper(), 'SUCCESS')
	data = self.db.fetch(self.keyname)
	self.assertEqual(data.keyvalue, self.keyvalue)

	self.keyvalue = 'value2'
	so = self.db.update(self.keyname, self.keyvalue)
	self.assertEqual(str(so.status).upper(), 'SUCCESS')
	data = self.db.fetch(self.keyname)
	self.assertEqual(data.keyvalue, self.keyvalue)

    def tearDown(self):
	data = self.db.delete(keyname=self.keyname)
	self.assertEqual(str(data.status).upper(), 'SUCCESS')
	data = self.db.delete()
	self.assertEqual(str(data.status).upper(), 'SUCCESS')

class ComplexTestCase1(unittest.TestCase):
    def setUp(self):
	import uuid
	
	self.projectid = str(uuid.uuid4())
	self.db = DatabaseAPI(__url__, project_id=self.projectid)
	pass
	
    def runTest(self):
	self.items = {}
	
	for i in xrange(0,100):
	    keyname = 'key%s' % (i)
	    self.items[keyname] = '0'
	    so = self.db.create(keyname, self.items[keyname])
	    self.assertEqual(str(so.status).upper(), 'SUCCESS')
	
	    data = self.db.fetch(keyname)
	    self.assertEqual(data.keyvalue, self.items[keyname])

	    data = self.db.count()
	    self.assertEqual(data.count, i+1)
	    
	for k,v in self.items.iteritems():
	    v = '%s' % (int(v) + 1)
	    so = self.db.update(k, v)
	    self.assertEqual(str(so.status).upper(), 'SUCCESS')
	    data = self.db.fetch(k)
	    self.assertEqual(data.keyvalue, v)

    def tearDown(self):
	data = self.db.delete()
	self.assertEqual(str(data.status).upper(), 'SUCCESS')

def main():
    unittest.main()

if (__name__ == "__main__"):
    import uuid
    from optparse import OptionParser
    
    parser = OptionParser("usage: %prog options")
    parser.add_option('-a', '--address', dest='address', action="store", help="http://0.0.0.0:9999")
    
    options, args = parser.parse_args()
    
    __address__ = 'project_%s' % (str(uuid.uuid4()))
    if (options.address):
	__address__ = options.address
	__url__ = 'http://%s' % (__address__)
 
    main()
    