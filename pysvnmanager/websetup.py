"""Setup the pySvnManager application"""
import logging

from paste.deploy import appconfig
from pylons import config
from shutil import copyfile
import os
from pkg_resources import resource_filename

from pysvnmanager.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup pysvnmanager here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    here = config['here']

    if not os.path.exists(here+'/config'):
        os.mkdir(here+'/config')
    if not os.path.exists(here+'/config/RCS'):
        os.mkdir(here+'/config/RCS')
    filelist = ['svn.access', 'svn.passwd', 'localconfig.py']
    for f in filelist:
        src  = resource_filename('pysvnmanager', 'config/' + f+'.in')
        dest = here+'/config/' + f
        if os.path.exists(dest):
            log.warning("Warning: %s already exist, ignored." % f)
        else:
            copyfile(src, dest)

