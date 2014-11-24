import os, sys
import json
import requests

from vyperlogix import misc
from vyperlogix.misc import _utils
from vyperlogix.classes.SmartObject import SmartObject
from vyperlogix.classes.MagicObject import MagicObject2

__normalize_uri__ = lambda uri:(uri+'/') if (not uri.endswith('/')) else uri
normalize_uri = lambda uri:'http://%s' % (__normalize_uri__(uri)) if ( (uri.find('http://') == -1) and (uri.find('https://') == -1) ) else __normalize_uri__(uri)

class DatabaseAPI(MagicObject2):
    def __init__(self, uri, project_id=None, silently=True, verify=False):
        self.__project_id__ = project_id
        self.__uri__ = uri
        self.__silently__ = silently
        self.__verify__ = verify
        self.is_using_ssl = self.__uri__.find('https://') > -1
        self.__headers__ = {"content-type": "application/json"}
        self.basename = 'database'
        
        if (self.is_using_ssl and not self.__verify__):
            import requests.packages.urllib3 as urllib3
            urllib3.disable_warnings()

    def __call__(self,*args,**kwargs):
        from vyperlogix.lists import ConsumeableList
        n = ConsumeableList(self.n)
        items = []
        for item in n:
            if (item.startswith('__') and item.endswith('__')):
                break
            items.append(item)
        s = 'self.__handler__(%s, *args,**kwargs)' % ('[%s]'%(','.join(['"%s"'%(i) for i in items])))
        try:
            results = eval(s,globals(),locals())
        except Exception:
            pass
        return results

    def __getattr__(self,name):
        normalize = lambda n:'__%s__'%(n)
        if name in ('__str__','__repr__'): return lambda:'instance of %s at %s' % (str(self.__class__),id(self))
        __name__ = normalize(name)
        if (self.__dict__.has_key(__name__)):
            self.__reset_magic__()
            return self.__dict__[__name__]
        if not self.__dict__.has_key('n'):self.n=[]
        if (name == self.basename):
            self.__reset_magic__()
            self.n.append(name)
            return self
        self.n.append(name)
        return self

    def __handler__(self,items,*args,**kwargs):
        uri = []
        parms = []
        uri.append(items[0])
        if (uri[0] == self.basename):
            uri.append(self.username)
            uri.append(self.password)
            for item in items[1:]:
                uri.append(item)
            for arg in args:
                uri.append(arg)
            for k,v in kwargs.iteritems():
                parms.append('%s=%s'%(k,v))
            if (len(parms) > 0):
                uri.append('?%s'%('&'.join(parms)))
        __uri__ = '/'.join(uri)
        if (self.is_using_ssl):
            r = requests.get(normalize_uri(self.uri)+__uri__,verify=self.__verify__,headers=self.__headers__)
        else:
            r = requests.get(normalize_uri(self.uri)+__uri__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot retrieve the requested value at this time due to the following: %s' % (status))
        return SmartObject(d)

    def create(self, keyname, keyvalue):
        if (self.is_using_ssl):
            r = requests.post(normalize_uri(self.uri)+'create',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname,'keyvalue':keyvalue}),verify=self.__verify__,headers=self.__headers__)
        else:
            r = requests.post(normalize_uri(self.uri)+'create',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname,'keyvalue':keyvalue}),headers=self.__headers__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (not self.__silently__) and (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot create the requested key/value at this time due to the following: %s' % (status))
        return SmartObject(d)

    def update(self, keyname, keyvalue):
        if (self.is_using_ssl):
            r = requests.put(normalize_uri(self.uri)+'update',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname,'keyvalue':keyvalue}),verify=self.__verify__,headers=self.__headers__)
        else:
            r = requests.put(normalize_uri(self.uri)+'update',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname,'keyvalue':keyvalue}),headers=self.__headers__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (not self.__silently__) and (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot update the requested key/value at this time due to the following: %s' % (status))
        return SmartObject(d)

    def fetch(self, keyname):
        if (self.is_using_ssl):
            r = requests.get(normalize_uri(self.uri)+'fetch/%s/%s' % (self.__project_id__,keyname),verify=self.__verify__,headers=self.__headers__)
        else:
            r = requests.get(normalize_uri(self.uri)+'fetch/%s/%s' % (self.__project_id__,keyname),headers=self.__headers__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (not self.__silently__) and (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot fetch the requested keyname at this time due to the following: %s' % (status))
        return SmartObject(d)

    def count(self):
        if (self.is_using_ssl):
            r = requests.get(normalize_uri(self.uri)+'count/%s' % (self.__project_id__),verify=self.__verify__,headers=self.__headers__)
        else:
            r = requests.get(normalize_uri(self.uri)+'count/%s' % (self.__project_id__),headers=self.__headers__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (not self.__silently__) and (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot fetch the requested keyname at this time due to the following: %s' % (status))
        return SmartObject(d)

    def delete(self, keyname=None):
        if (self.is_using_ssl):
            if (keyname):
                r = requests.delete(normalize_uri(self.uri)+'delete',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname}),verify=self.__verify__,headers=self.__headers__)
            else:
                r = requests.delete(normalize_uri(self.uri)+'delete',data=json.dumps({'project_id':self.__project_id__}),verify=self.__verify__,headers=self.__headers__)
        else:
            if (keyname):
                r = requests.delete(normalize_uri(self.uri)+'delete',data=json.dumps({'project_id':self.__project_id__,'keyname':keyname}),headers=self.__headers__)
            else:
                r = requests.delete(normalize_uri(self.uri)+'delete',data=json.dumps({'project_id':self.__project_id__}),headers=self.__headers__)
        if (r.status_code != 200):
            r.raise_for_status()
        d = r.json()
        status = d.get('status',None)
        if (not self.__silently__) and (str(status).upper() != 'SUCCESS'):
            raise ValueError('Cannot fetch the requested keyname at this time due to the following: %s' % (status))
        return SmartObject(d)

if (__name__ == '__main__'):
    from optparse import OptionParser

    parser = OptionParser("usage: %prog options")
    parser.add_option('-a', '--address', dest='address', action="store", help="http://0.0.0.0:9999")
    parser.add_option('-p', '--projectid', dest='project', action="store", help="project id")
    parser.add_option('-k', '--keyname', dest='keyname', action="store", help="keyname")
    parser.add_option('-v', '--keyvalue', dest='keyvalue', action="store", help="keyvalue")

    options, args = parser.parse_args()

    import uuid

    __projectid__ = 'project_%s' % (str(uuid.uuid4()))
    if (options.project):
        __projectid__ = options.project

    print 'project_id=%s' % (__projectid__)

    if (options.address):
        db = DatabaseAPI(options.address, project_id=__projectid__)

        if (options.keyname and options.keyvalue):
            print 'Create:',
            so = db.create(options.keyname, options.keyvalue)
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the create function.'

            print 'Count:',
            so = db.count()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the first count function.'
            assert str(so.count).isdigit() == True, 'Something wrong with the count function because count value are not digits.'
            assert so.count == 1, 'Something wrong with the count function because the count value should be 1 but is not.'

            print 'Fetch:',
            so = db.fetch(options.keyname)
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the fetch function.'
            assert so.keyname == options.keyname, 'Something wrong with the fetch for keyname.'
            assert so.keyvalue == options.keyvalue, 'Something wrong with the fetch for keyvalue.'

            print 'Update:',
            so = db.update(options.keyname, options.keyvalue+'_'+str(uuid.uuid4()))
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the update function.'

            print 'Delete:',
            so = db.delete(options.keyname)
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the delete function.'

            print 'Count:',
            so = db.count()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the second count function.'
            assert str(so.count).isdigit() == True, 'Something wrong with the count function because count value are not digits.'
            assert so.count == 0, 'Something wrong with the count function because the count value should be 0 but is not.'

            print 'Create:',
            so = db.create(options.keyname+'1', options.keyvalue)
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the create function.'

            print 'Count:',
            so = db.count()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the first count function.'
            assert str(so.count).isdigit() == True, 'Something wrong with the count function because count value are not digits.'
            assert so.count == 1, 'Something wrong with the count function because the count value should be 1 but is not.'

            print 'Create:',
            so = db.create(options.keyname+'2', options.keyvalue)
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the create function.'

            print 'Count:',
            so = db.count()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the first count function.'
            assert str(so.count).isdigit() == True, 'Something wrong with the count function because count value are not digits.'
            assert so.count == 2, 'Something wrong with the count function because the count value should be 1 but is not.'

            print 'Delete:',
            so = db.delete()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the delete function.'

            print 'Count:',
            so = db.count()
            print so
            assert str(so.status).upper() == 'SUCCESS', 'Something wrong with the second count function.'
            assert str(so.count).isdigit() == True, 'Something wrong with the count function because count value are not digits.'
            assert so.count == 0, 'Something wrong with the count function because the count value should be 0 but is not.'

        elif (options.keyname):
            so = db.fetch(options.keyname)
            print so
        else:
            print >> sys.stderr, 'ERROR: Cannot proceed without either the keyname or both the keyname and keyvalue.'
    else:
        print >> sys.stderr, 'ERROR: Cannot proceed without the address of the web service.'
