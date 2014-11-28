import os
import sys
import web

import Queue
import threading

import json
import urllib

__version__ = '2.0.0'

import logging
from logging import handlers

class MyTimedRotatingFileHandler(handlers.TimedRotatingFileHandler):
    def __init__(self, filename, maxBytes=0, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        handlers.TimedRotatingFileHandler.__init__(self, filename=filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)
        self.maxBytes = maxBytes

    def shouldRollover(self, record):
        response = handlers.TimedRotatingFileHandler.shouldRollover(self, record)
        if (response == 0):
            if self.stream is None:                 # delay was set...
                self.stream = self._open()
            if self.maxBytes > 0:                   # are we rolling over?
                msg = "%s\n" % self.format(record)
                try:
                    self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
                    if self.stream.tell() + len(msg) >= self.maxBytes:
                        return 1
                except:
                    pass
            return 0
        return response

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

verbose = False
import imp
if (hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")):
    import zipfile
    import pkg_resources

    import re
    __regex_libname__ = re.compile(r"(?P<libname>.*)_2_7\.zip", re.MULTILINE)

    my_file = pkg_resources.resource_stream('__main__',sys.executable)

    import tempfile
    __dirname__ = os.path.dirname(tempfile.NamedTemporaryFile().name)

    zip = zipfile.ZipFile(my_file)
    files = [z for z in zip.filelist if (__regex_libname__.match(z.filename))]
    for f in files:
        libname = f.filename
        data = zip.read(libname)
        fpath = os.sep.join([__dirname__,os.path.splitext(libname)[0]])
        __is__ = False
        if (not os.path.exists(fpath)):
            os.mkdir(fpath)
        else:
            fsize = os.path.getsize(fpath)
            if (fsize != f.file_size):
                __is__ = True
        fname = os.sep.join([fpath,libname])
        if (verbose):
            print 'INFO: fname is "%s".' % (fname)
            print 'INFO: __is__ is "%s".' % (__is__)
        if (not os.path.exists(fname)) or (__is__):
            file = open(fname, 'wb')
            file.write(data)
            file.flush()
            file.close()
            if (verbose):
                print 'INFO: fname(2) is "%s".' % (fname)
        __module__ = fname

        import zipextimporter
        zipextimporter.install()
        sys.path.insert(0, __module__)
    print 'BEGIN:'
    for f in sys.path:
        print f
    print 'END!!'
    
from vyperlogix import misc
from vyperlogix.misc import _utils
from vyperlogix.misc import ObjectTypeName

urls = (
    '/', 'WebRoot',
    '/(js|css|images)/(.*)', 'StaticRoot',
    '/create/', 'DatabaseBackend',
    '/create', 'DatabaseBackend',
    '/update/', 'DatabaseBackend',
    '/update', 'DatabaseBackend',
    '/fetch/(.+)', 'DatabaseBackend',
    '/count/(.+)', 'DatabaseAnalytics',
    '/delete', 'DatabaseBackend',
    '/setwindowsagentaddr', 'Nothing',
    '/setwindowsagentaddr/', 'Nothing',
)

### Templates
render = web.template.render('templates', base='base')

web.template.Template.globals.update(dict(
    datestr = web.datestr,
    render = render
))

def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.  This message may be seen whenever someone tries to issue a negative number as part of the REST URL Signature and this is just not allowed at this time.")

__index__ = '''
<html>
<head>
    <title>(c). Copyright 2014, VyperLogix Corporation, All Rights Reserved.</title>
    <style>
        #menu {
            width: 200px;
            float: left;
        }
    </style>
</head>
<body>

<ul id="menu">
    <li><a href="/">Home</a></li>
</ul>

<p><b>UNAUTHORIZED ACCESS (%s)</b></p>

</body>
</html>
'''

class WebRoot:
    __webroot__ = os.path.abspath(os.curdir)+os.sep+'www'
    def GET(self):
        """ Show page """
        s = 'database-api %s' % (__version__)
        web.header('Content-Type', 'text/html')
        index_html = WebRoot.__webroot__+os.sep+'index.html'
        index_htm = WebRoot.__webroot__+os.sep+'index.htm'
        is_index_html = (os.path.exists(index_html) and (os.path.isfile(index_html)))
        is_index_htm = (os.path.exists(index_htm) and (os.path.isfile(index_htm)))
        content = __index__
        if (os.path.exists(WebRoot.__webroot__) and (is_index_html or is_index_htm) ):
            if (is_index_html):
                content = ''.join(open(index_html).readlines())
            elif (is_index_htm):
                content = ''.join(open(index_htm).readlines())
        else:
            content = __index__ % (os.path.abspath(os.curdir))
        return content

class StaticRoot:
    __webroot__ = os.path.abspath(os.curdir)+os.sep+'www'
    def GET(self, media=None, fname=None):
        if (media == 'js'):
            web.header('Content-Type', 'application/javascript')
        try:
            fpath = os.sep.join([StaticRoot.__webroot__,media,fname])
            f = open(fpath, 'r')
            return f.read()
        except:
            raise web.notfound()
##############################################################
from optparse import OptionParser

parser = OptionParser("usage: %prog options 0.0.0.0:9999")
parser.add_option('-s', '--syncdb', dest='syncdb', action="store_true", help="should the database be created?")
parser.add_option('-r', '--repl', dest='repl', action="store_true", help="start a REPL with access to your models")
parser.add_option('-d', '--dumpdata', dest='dumpdata', action="store_true", help="django dumpdata")
parser.add_option('-i', '--inspectdb', dest='inspectdb', action="store_true", help="django inspectdb")
parser.add_option('-v', '--verbose', dest='verbose', help="verbose", action="store_true")
parser.add_option('-a', '--address', dest='address', action="store", help="valid ip address and port in the form of 0.0.0.0:9999")
parser.add_option('-c', '--conf', dest='config', action="store", help="location of database-api.conf file.")
parser.add_option('-l', '--logging', dest='logging', action="store", help="logging debug, info, warning, error or critical.")
parser.add_option('-p', '--logpath', dest='logpath', action="store", help="fully qualified path for the log file, must be accessible to the runtime user context.")
parser.add_option('-w', '--webroot', dest='webroot', action="store", help="fully qualified path for the webroot, must be accessible to the runtime user context.")
parser.add_option('-e', '--ssl', dest='usessl', help="Use self-signed SSL Certs for HTTPS rather than HTTP.", action="store_true")

options, args = parser.parse_args()

__dbengine__ = 'django.db.backends.mysql'
__dbname__ = 'horizon'
__dbuser__ = 'root'
__dbpassword__ = 'password'
__dbhost__ = '127.0.0.1'
__dbport__ = '3306'

__section__ = 'horizon-database-config'

if options.config:
    print >> sys.stderr, 'options.config=%s' % (options.config)
    if (os.path.exists(options.config) and os.path.isfile(options.config)):
        import ConfigParser

        config = ConfigParser.RawConfigParser()
        config.read(options.config)

        __dbengine__ = config.get(__section__, 'engine')
        __dbname__ = config.get(__section__, 'name')
        __dbuser__ = config.get(__section__, 'user')
        __dbpassword__ = config.get(__section__, 'password')
        __dbhost__ = config.get(__section__, 'host')
        __dbport__ = config.get(__section__, 'port')

##############################################################

DATABASES = {
    'default': {
        'ENGINE': __dbengine__,
        'NAME': __dbname__,
        'USER' : __dbuser__,
        'PASSWORD' : __dbpassword__,
        'HOST' : __dbhost__,
        'PORT' : __dbport__,
    }
}

LOG_FILENAME = os.sep.join([os.path.dirname(sys.argv[0]),'database-api.log'])

if (options.logpath):
    __fpath__ = options.logpath
    if (os.path.isfile(options.logpath)):
        __fpath__ = os.path.dirname(__fpath__)
    LOG_FILENAME = os.sep.join([__fpath__,'database-api.log'])
elif (not _utils.isBeingDebugged):
    print >> sys.stderr, 'ERROR: Cannot proceed without a fully qualified logpath using the -p or --logpath option.'
    sys.exit(1)

logger = logging.getLogger('database-api')
handler = logging.FileHandler(LOG_FILENAME)
handler = handlers.TimedRotatingFileHandler(LOG_FILENAME, when='d', interval=1, backupCount=30, encoding=None, delay=False, utc=False)
handler = MyTimedRotatingFileHandler(LOG_FILENAME, maxBytes=1000000, when='d', backupCount=30)
handler = handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=30, encoding=None, delay=False)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
__level__ = logging.INFO
if (options.logging):
    if (options.logging == 'debug'):
        __level__ = logging.DEBUG
    elif (options.logging == 'warning'):
        __level__ = logging.WARNING
    elif (options.logging == 'error'):
        __level__ = logging.ERROR
    elif (options.logging == 'critical'):
        __level__ = logging.CRITICAL
handler.setLevel(__level__)
logger.addHandler(handler) 
print 'Logging to "%s".' % (handler.baseFilename)

if (_utils.isBeingDebugged):
    ch = logging.StreamHandler()
    ch_format = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(ch_format)
    ch.setLevel(__level__)
    logger.addHandler(ch)
else:
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl
    
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

logger.info('isBeingDebugged=%s' % (_utils.isBeingDebugged))

logging.getLogger().setLevel(__level__)
print '__level__=%s [%s]' % (__level__,'DEBUG' if (__level__ == logging.DEBUG) else 'INFO' if (__level__ == logging.INFO) else 'WARNING' if (__level__ == logging.WARNING) else 'ERROR' if (__level__ == logging.ERROR) else 'CRITICAL' if (__level__ == logging.CRITICAL) else 'UNKNOWN')

if (options.webroot):
    if (os.path.exists(options.webroot) and os.path.isdir(options.webroot)):
        Index.__webroot__ = options.webroot
        logger.info('Webroot is now "%s".' % (Index.__webroot__))

class CustomJSONENcoder(json.JSONEncoder):
    def default(self, o):
        obj = {'__class__':ObjectTypeName.typeClassName(o)}
        try:
            for k,v in o.__dict__.iteritems():
                obj[k] = v
        except AttributeError:
            if (ObjectTypeName.typeClassName(o) == 'file'):
                obj['name'] = o.name
                obj['mode'] = o.mode
            else:
                pass
            pass
        return obj

class Nothing:
    def POST(self):
        web.header('Content-Type', 'application/json')
        reasons = []
        url = web.ctx.home + web.ctx.path + web.ctx.query
        content = json.dumps(web.ctx.env,cls=CustomJSONENcoder)
        logger.info('%s --> %s %s' % (url,content,web.data()))
        content = json.dumps({'status':''.join(reasons)})
        return content

from standalone.conf import settings

try:
    settings = settings(
        DATABASES = DATABASES
    )
except:
    pass

from standalone import models

class Index(models.StandaloneModel):
    projectid = models.CharField(max_length=128,blank=False,unique=True,primary_key=False)

    class Meta:
        db_table = u'index'
    
    def details(self):
        from django.forms.models import model_to_dict
        return str(model_to_dict(self))

class Keys(models.StandaloneModel):
    keyname = models.CharField(max_length=128,blank=False,unique=True,primary_key=False)

    class Meta:
        db_table = u'keys'
    
    def details(self):
        from django.forms.models import model_to_dict
        return str(model_to_dict(self))

class Values(models.StandaloneModel):
    keyvalue = models.TextField(max_length=1024,blank=False,unique=False,primary_key=False)

    class Meta:
        db_table = u'values'
    
    def details(self):
        from django.forms.models import model_to_dict
        return str(model_to_dict(self))

class KeyedValues(models.StandaloneModel):
    projectid = models.ForeignKey(Index,to_field='id')
    keyid = models.ForeignKey(Keys,to_field='id')
    valueid = models.ForeignKey(Values,to_field='id')
    created_at = models.DateTimeField(blank=False)
    modified_at = models.DateTimeField(blank=False)
    class Meta:
        db_table = u'keyedvalues'

    def details(self):
        from django.forms.models import model_to_dict
        return str(model_to_dict(self))

def normalize_item(item):
    d = item.__dict__
    d['created_at'] = _utils.getAsSimpleDateStr(d['created_at'],fmt=_utils.formatMySQLDateTimeStr())
    d['modified_at'] = _utils.getAsSimpleDateStr(d['modified_at'],fmt=_utils.formatMySQLDateTimeStr())
    try:
        d['keyname'] = item.keyid.keyname
        del d['keyid_id']
    except:
        pass
    try:
        d['keyvalue'] = item.valueid.keyvalue
        del d['valueid_id']
    except:
        pass
    try:
        del d['_keyid_cache']
    except:
        pass
    try:
        del d['_valueid_cache']
    except:
        pass
    del d['_state']
    return d

class DatabaseAnalytics:
    def GET(self,items=None):
        web.header('Content-Type', 'application/json')
        reasons = []
        response = {}
        toks = items.split('/')
        project_id = None
        if (len(toks) == 1):
            project_id = toks[0]
        while (1):
            try:
                idx = Index.objects.get(projectid=project_id)
                break
            except:
                idx = None
                break
        if (idx):
            try:
                if (project_id):
                    items = KeyedValues.objects.filter(projectid=idx.id)
                    reasons.append('SUCCESS')
                else:
                    items = []
                    reasons.append('FAILURE - Cannot count all items, please specify a project_id and try again.')
                response['count'] = len(items)
            except Exception, ex:
                reasons.append('ERROR: %s' % (ex))
        response['status'] = ''.join(reasons)
        content = json.dumps(response)
        return content

class DatabaseBackend:
    def GET(self,items=None):
        web.header('Content-Type', 'application/json')
        reasons = []
        response = {}
        toks = items.split('/')
        project_id = None
        keyname = None
        if (len(toks) == 2):
            keyname = toks[1]
        if (len(toks) == 1):
            project_id = toks[0]
        logger.info('project_id=%s, keyname=%s' % (project_id,keyname))
        try:
            idx = None
            if (project_id):
                try:
                    idx = Index.objects.get(projectid=project_id)
                except:
                    idx = None
            key = None
            if (keyname):
                try:
                    key = Keys.objects.get(keyname=keyname)
                except:
                    key = None
            __items__ = []
            if (idx and key):
                items = KeyedValues.objects.get(projectid=idx.id,keyid=key.id)
                if (items.keyid.keyname == keyname):
                    d = normalize_item(items)
                    for k,v in d.iteritems():
                        response[k] = v
                    reasons.append('SUCCESS')
                else:
                    reasons.append('FAILURE')
            elif (idx):
                items = KeyedValues.objects.filter(projectid=idx.id)
                for item in items:
                    __items__.append(normalize_item(item))
            response['items'] = __items__
            reasons.append('SUCCESS')
        except Exception, ex:
            reasons.append('ERROR: %s' % (ex))
        response['status'] = ''.join(reasons)
        content = json.dumps(response)
        return content

    def PUT(self):
        web.header('Content-Type', 'application/json')
        reasons = []
        response = {}
        data = json.loads(web.data())

        project_id = data.get('project_id',None)
        keyname = data.get('keyname',None)
        keyvalue = data.get('keyvalue',None)
        logger.info('project_id=%s, keyname=%s, keyvalue=%s' % (project_id,keyname,keyvalue))
        __is__ = False
        try:
            idx = Index.objects.get(projectid=project_id)
        except:
            idx = None
        try:
            key = Keys.objects.get(keyname=keyname)
        except:
            key = None
        if (idx and key):
            try:
                item = KeyedValues.objects.get(projectid=idx.id,keyid=key.id)
            except:
                __is__ = True
            if (not __is__) and (item.keyid.keyname == keyname):
                item.valueid.keyvalue = keyvalue
                item.modified_at = _utils.today_localtime()
                item.save()
                reasons.append('SUCCESS')
            else:
                try:
                    while (1):
                        try:
                            key = Keys.objects.get(keyname=keyname)
                            break
                        except:
                            key = Keys()
                            key.keyname = keyname
                            key.save()
    
                    while (1):
                        try:
                            value = Values.objects.get(keyvalue=keyvalue)
                            break
                        except:
                            value = Values()
                            value.keyvalue = keyvalue
                            value.save()
    
                    kv = KeyedValues()
                    kv.projectid = idx
                    kv.keyid = key
                    kv.valueid = value
                    kv.created_at = _utils.today_localtime()
                    kv.modified_at = _utils.today_localtime()
                    kv.save()
                    reasons.append('SUCCESS')
                except Exception, ex:
                    reasons.append('ERROR: %s' % (ex))

        response['status'] = ''.join(reasons)
        content = json.dumps(response)
        return content

    def DELETE(self):
        web.header('Content-Type', 'application/json')
        reasons = []
        response = {}
        data = json.loads(web.data())

        project_id = data.get('project_id',None)
        keyname = data.get('keyname',None)
        logger.info('project_id=%s, keyname=%s' % (project_id,keyname))

        try:
            if (project_id):
                while (1):
                    try:
                        idx = Index.objects.get(projectid=project_id)
                        break
                    except:
                        idx = Index()
                        idx.projectid = project_id
                        idx.save()
                if (not keyname):
                    __items__ = KeyedValues.objects.filter(projectid=idx.id)
                    for item in __items__:
                        item.delete()
                    reasons.append('SUCCESS')
                else:
                    while (1):
                        try:
                            key = Keys.objects.get(keyname=keyname)
                            break
                        except:
                            key = Keys()
                            key.keyname = keyname
                            key.save()
                    try:
                        item = KeyedValues.objects.get(projectid=idx.id,keyid=key.id)
                        if (item.keyid.keyname == keyname):
                            item.delete()
                            reasons.append('SUCCESS')
                        else:
                            reasons.append('FAILURE')
                    except Exception, ex:
                        reasons.append('ERROR: %s' % (ex))
            else:
                reasons.append('FAILURE')
        except Exception, ex:
            reasons.append('ERROR: %s' % (ex))

        response['status'] = ''.join(reasons)
        content = json.dumps(response)
        return content

    def POST(self,action=None):
        web.header('Content-Type', 'application/json')
        reasons = []
        response = {}
        data = json.loads(web.data())

        project_id = data.get('project_id',None)
        keyname = data.get('keyname',None)
        keyvalue = data.get('keyvalue',None)
        logger.info('project_id=%s, keyname=%s, keyvalue=%s' % (project_id,keyname,keyvalue))
        __is__ = False
        while (1):
            try:
                idx = Index.objects.get(projectid=project_id)
                break
            except:
                idx = Index()
                idx.projectid = project_id
                idx.save()
        while (1):
            try:
                key = Keys.objects.get(keyname=keyname)
                break
            except:
                key = Keys()
                key.keyname = keyname
                key.save()
        try:
            item = KeyedValues.objects.get(projectid=idx.id,keyid=key.id)
        except:
            __is__ = True
        if (not __is__) and (item.keyid.keyname == keyname):
            items.valueid.keyvalue = keyvalue
            items.modified_at = _utils.today_localtime()
            items.save()
            reasons.append('SUCCESS')
        else:
            try:
                while (1):
                    try:
                        key = Keys.objects.get(keyname=keyname)
                        break
                    except:
                        key = Keys()
                        key.keyname = keyname
                        key.save()

                while (1):
                    try:
                        value = Values.objects.get(keyvalue=keyvalue)
                        break
                    except:
                        value = Values()
                        value.keyvalue = keyvalue
                        value.save()

                kv = KeyedValues()
                kv.projectid = idx
                kv.keyid = key
                kv.valueid = value
                kv.created_at = _utils.today_localtime()
                kv.modified_at = _utils.today_localtime()
                kv.save()
                reasons.append('SUCCESS')
            except Exception, ex:
                reasons.append('ERROR: %s' % (ex))

        response['status'] = ''.join(reasons)
        content = json.dumps(response)
        return content

if (options.usessl):
    try:
        from web.wsgiserver import CherryPyWSGIServer

        CherryPyWSGIServer.ssl_certificate = os.path.abspath("./server.crt")
        CherryPyWSGIServer.ssl_private_key = os.path.abspath("./server.key.insecure")
    except ImportError:
        pass

app = web.application(urls, globals())
app.notfound = notfound

def does_database_exist(__databases__):
    import MySQLdb
    __is__ = True
    __exception__ = False
    __reason__ = None
    try:
        __default__ = __databases__.get('default',None)
        if (__default__):
            __host__ = __default__.get('HOST',None)
            __user__ = __default__.get('USER',None)
            __password__ = __default__.get('PASSWORD',None)
            __port__ = __default__.get('PORT',None)
            if (__port__):
                __port__ = int(str(__port__))
            __dbname__ = __default__.get('NAME',None)
            if (__host__ and __user__ and __password__ and __port__ and __dbname__):
                conn = MySQLdb.connect(host=__host__,user=__user__,passwd=__password__,port=__port__,db=__dbname__)
                conn.close()
            else:
                __is__ = None
                logger.error('(1) Database config is missing something, please make sure it is correct for your needs.')
        else:
            __is__ = False
    except Exception, ex:
        __is__ = False
        __exception__ = True
        __reason__ = str(ex)
        logger.error('(1) Database does not exist! Because: %s' % (__reason__))
    
    if ( (not __is__) and (__reason__.find('Unknown database') > -1) ):
        logger.info('Attempting to create the database')
        try:
            __default__ = __databases__.get('default',None)
            if (__default__):
                __host__ = __default__.get('HOST',None)
                __user__ = __default__.get('USER',None)
                __password__ = __default__.get('PASSWORD',None)
                __port__ = __default__.get('PORT',None)
                if (__port__):
                    __port__ = int(str(__port__))
                __dbname__ = __default__.get('NAME',None)
                if (__host__ and __user__ and __password__ and __port__ and __dbname__):
                    conn = MySQLdb.connect(host=__host__,user=__user__,passwd=__password__,port=__port__)
                    logger.info('Successful connection to the database server.')
                    cursor = conn.cursor()
                    cursor.execute('CREATE DATABASE %s;' % (__dbname__))
                    conn.close()
                    logger.info('Creating tables in %s.' % (__dbname__))
                    call_command('syncdb')
                else:
                    __is__ = None
                    logger.error('(2) Database config is missing something, please make sure it is correct for your needs.')
            else:
                __is__ = False
        except Exception, ex:
            __is__ = False
            __exception__ = True
            __reason__ = str(ex)
            logger.error('(2) Database does not exist! Because: %s' % (__reason__))
        
    return __is__

if (__name__ == '__main__'):
    '''
    python database-api.py 127.0.0.1:9999
    '''
    import re
    import signal

    from django.core.management import call_command

    if options.syncdb:
        call_command('syncdb')
        _utils.terminate('Terminated: syncdb is complete.')
    elif options.repl:
        call_command('shell')
        _utils.terminate('Terminated: shell is complete.')
    elif options.dumpdata:
        call_command('dumpdata')
        _utils.terminate('Terminated: dumpdata is complete.')
    elif options.inspectdb:
        call_command('inspectdb')
        _utils.terminate('Terminated: inspectdb is complete.')

    __re__ = re.compile(r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):([0-9]{1,5})", re.MULTILINE)

    #sys.argv = [sys.argv[0]]

    if (options.address and __re__.search(options.address)):
        sys.argv.insert(1, options.address)
    elif (not __re__.search(sys.argv[-1])):
        sys.argv.insert(1, '127.0.0.1:9192')

    logger.info('sys.argv=%s' % (sys.argv))

    def __init__():
        logger.info('database-api %s started !!!' % (__version__))
        app.run()

    __count__ = 2
    while (__count__ > 0):
        __is__ = does_database_exist(DATABASES)
        if (__is__ == True):
            t = threading.Thread(target=__init__)
            t.daemon = False
            t.start()
            break
        elif (__is__ is None):
            logger.warning('Database config seems invalid, please check it again!')
            _utils.terminate('Terminated: Database config in error.')
        else:
            __count__ -= 1
            logger.warning('(%s) Database does not exist!' % (__count__))
            if (__count__ == 0):
                _utils.terminate('Terminated: Database does not exist or config in error.')

