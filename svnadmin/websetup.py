"""Setup the svnadmin application"""
import logging

from paste.deploy import appconfig
from pylons import config
from shutil import copyfile
import os
from pkg_resources import resource_filename

from svnadmin.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup svnadmin here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    here = config['here']

    if not os.path.exists(here+'/config'):
        os.mkdir(here+'/config')
    filelist = ['svn.access', 'svn.passwd', 'localconfig.py']
    for f in filelist:
        src  = resource_filename('svnadmin', 'config/' + f+'.in')
        dest = here+'/config/' + f
        if os.path.exists(dest):
            log.warning("Warning: %s already exist, ignored." % f)
        else:
            copyfile(src, dest)

