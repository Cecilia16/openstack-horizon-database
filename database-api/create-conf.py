import ConfigParser

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
__section__ = 'horizon-database-config'
config.add_section(__section__)
config.set(__section__, 'ENGINE', 'django.db.backends.mysql')
config.set(__section__, 'NAME', 'horizon')
config.set(__section__, 'USER', 'root')
config.set(__section__, 'PASSWORD', 'password')
config.set(__section__, 'HOST', '127.0.0.1')
config.set(__section__, 'PORT', '3306')

fname = '%s.conf' % (__section__)
# Writing our configuration file to 'example.cfg'
with open(fname, 'wb') as configfile:
    config.write(configfile)
