import os, sys

import tempfile

tmp = tempfile.gettempdir()
fpath = os.sep.join([tmp,'process-list.txt'])

from optparse import OptionParser

parser = OptionParser("usage: %prog options 0.0.0.0:9999")
parser.add_option('-n', '--name', dest='name', action="store", help="process name")

options, args = parser.parse_args()

if (options.name):
    os.system('ps -ef | grep "%s" > "%s"' % (options.name,fpath))
    
    if (os.path.exists(fpath) and os.path.isfile(fpath)):
        fIn = open(fpath,mode='r')
        for item in fIn:
            toks = item.strip().split()
            print >> sys.stdout, 'INFO: Killing pid %s' % (toks[1])
            os.system('kill -9 %s' % (toks[1]))
        fIn.close()
        os.remove(fpath)
else:
    print >> sys.stderr, 'ERROR: Cannot proceed without a process name using the -n or --name option.'
    sys.exit(1)

    