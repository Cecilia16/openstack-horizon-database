import ConfigParser

__section__ = 'horizon-database-config'
fname = '%s.conf' % (__section__)

config = ConfigParser.RawConfigParser()
config.read(fname)

__dbengine__ = config.get(__section__, 'engine')
__dbname__ = config.get(__section__, 'name')
__dbuser__ = config.get(__section__, 'user')
__dbpassword__ = config.get(__section__, 'password')
__dbhost__ = config.get(__section__, 'host')
__dbport__ = config.get(__section__, 'port')

print '__dbengine__=%s' % (__dbengine__)
print '__dbname__=%s' % (__dbname__)
print '__dbuser__=%s' % (__dbuser__)
print '__dbpassword__=%s' % (__dbpassword__)
print '__dbhost__=%s' % (__dbhost__)
print '__dbport__=%s' % (__dbport__)

