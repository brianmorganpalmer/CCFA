import os
import sys
import random
import socket
from pprint import pformat

import setuptools
from django.utils.crypto import get_random_string

from . import (
    settings
)

here = os.path.dirname(os.path.realpath(__file__))
local_settings_file = os.path.join(here, "local_settings.py")
GRANT_TEMPLATE = \
'''create database %(NAME)s;
grant all privileges on %(NAME)s.* 
  to '%(USER)s'@'%(myhost)s' 
  identified by '%(PASSWORD)s'; 
flush privileges;

'''


def save_settings(path=local_settings_file, **kwargs):
    with open(path, 'a') as f:
        for key, value in kwargs.iteritems():
            print >> f, "%s = %s" %(key.upper(), pformat(value))

def randuser():
    return "".join( chr(random.randint(97,122)) for _ in range(8) )

def randpass():
    chrs = [
        chr(i) for i in [33]+range(35,39)+range(40,90)+range(97,122)+[124,126]
    ]
    return "".join( random.sample(chrs, 15) )


def curhost(settings_dict):
    host = settings_dict["HOST"] or "localhost"
    port = settings_dict["PORT"] or 3306
    if host in ["localhost", "127.0.0.1"]:
        return "localhost"
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        ret = s.getsockname()[0]
        s.close()
        return ret

def setup_mysql():
    cur_settings = settings.DATABASES["default"]
    db_settings = dict( ENGINE   = "django.db.backends.mysql",
                        NAME     = cur_settings["NAME"],
                        HOST     = cur_settings["HOST"],
                        PORT     = cur_settings["PORT"],
                        USER     = randuser(),
                        myhost   = curhost(cur_settings),
                        PASSWORD = randpass() )
    
    print >> sys.stderr, "Run the following on mysql as the root user:"
    print GRANT_TEMPLATE % db_settings
    
    db_settings.pop("myhost")
    print >> sys.stderr, "Adding db settings to %s" %(local_settings_file)
    save_settings(
        DATABASES={"default": db_settings}
    )
        

def setup_secret_keys():
    """Generate and save SECRET_KEY and NEVERCACHE key

    """
    save_settings( SECRET_KEY     = get_random_string(length=100),
                   NEVERCACHE_KEY = get_random_string(length=100) )



class LocalSetupCommand(setuptools.Command):
    
    description     = "Generate mysql settings for the anadama project"

    def run(self):
        setup_secret_keys()
        setup_mysql()
        print >> sys.stderr, "Thanks!"
    
    
    # cruft to get it to work with setup.py

    user_options    = [ ]
    help_options    = [ ]
    boolean_options = [ ]
    negative_opt    = { }
    default_format  = { }
    
    initialize_options = lambda self: None
    finalize_options = lambda self: None

